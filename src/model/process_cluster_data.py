import math
import pandas as pd
import numpy as np
from scipy.stats import f
from statsmodels.stats.libqsturng import psturng

# import src.controller.Controller


class Model:
    def __init__(self, path, controller):
        # read in csv data to dataframe
        self.data = pd.read_csv(path)
        self.controller = controller
        # calculated m/z of single charge
        self.summary_data = None
        self.position_data = None

    def start_process(self):
        self.controller.update_progress("Processing measurements:", "Calculating MH+")
        self.data["Center MH+"] = self.__calculate_mh1plus(
            self.data["z"], self.data["Center"]
        )
        self.data["Exposure"] = self.data["Exposure"].round(2)
        # calculate mean and varaince for MH+ of all replicate measruements
        self.summary_data = (
            self.data.groupby(
                [
                    "Protein",
                    "Sequence",
                    "Start",
                    "End",
                    "Exposure",
                    "State",
                    "MaxUptake",
                    "MHP",
                ]
            )
            .apply(self.__calc_summary_data, include_groups=False)
            .reset_index()
        )

        # calculate absolute and relative uptakes (zero time point is reference)
        self.summary_data = (
            self.summary_data.groupby(
                ["Protein", "Sequence", "Start", "End", "State", "MHP"]
            )
            .apply(self.__calc_fractional_uptakes, include_groups=False)
            .reset_index()
        )

        # calculate stats (ANOVA and Tukeyfor each protein position)
        self.position_data = (
            self.summary_data.groupby("Protein")
            .apply(self.__process_protein_to_position, include_groups=False)
            .reset_index()
        )

    def __calculate_mh1plus(self, z: int, center: float) -> float:
        f_center = center
        i_charge = z
        thompson = f_center * i_charge - ((z - 1) * 1.0078)
        return thompson

    def __calc_summary_data(self, group: pd.DataFrame) -> pd.Series:
        self.controller.update_progress(
            "Processing measurements:", "Summarising replicates"
        )

        weights = group["Inten"]
        count = len(group)

        average = np.average(group["Center MH+"], weights=weights)
        variance = np.average((group["Center MH+"] - average) ** 2, weights=weights)

        return pd.Series(
            {
                "Center Mean": average,
                "Center Variance": variance,
                "Count": int(count),
            }
        )

    def __calc_fractional_uptakes(self, group: pd.DataFrame) -> pd.DataFrame:
        self.controller.update_progress(
            "Processing measurements:", "Calculating fractional uptakes"
        )

        reference_uptake = group.loc[group["Exposure"] == 0].iloc[0]["Center Mean"]
        reference_variance = group.loc[group["Exposure"] == 0].iloc[0][
            "Center Variance"
        ]

        uptake = group[
            [
                "Exposure",
                "MaxUptake",
                "Center Mean",
                "Center Variance",
                "Count",
            ]
        ]
        uptake["Abs. Uptake Mean"] = group.apply(
            lambda x: x["Center Mean"] - reference_uptake, axis=1
        )
        uptake["Abs. Uptake Variance"] = group.apply(
            lambda x: x["Center Variance"] + reference_variance, axis=1
        )
        max_uptake = group.iloc[0]["MaxUptake"]
        uptake["Rel. Uptake Mean"] = uptake.apply(
            lambda x: x["Abs. Uptake Mean"] / max_uptake, axis=1
        )
        uptake["Rel. Uptake Variance"] = uptake.apply(
            lambda x: x["Abs. Uptake Variance"] / (max_uptake**2), axis=1
        )

        uptake = uptake.set_index("Exposure")
        return uptake

    def __process_protein_to_position(self, protein_group):
        max_position = protein_group["End"].max()
        self.controller.update_progress(protein_group.name, f"0/{max_position}")

        position_data = []
        for i in range(1, max_position + 1):
            if i % 10 == 0:
                self.controller.update_progress(
                    protein_group.name, f"{i}/{max_position}"
                )

            position_measurments = protein_group[
                (protein_group["Start"] < i)
                & (
                    protein_group["End"] >= i
                )  # ['Start'] < i (rather than <=) to remove N-term due to back exchange
            ]
            # at this point we have all states and exposures for all peptides covering this position
            if position_measurments.shape[0] > 0:
                anovas = (
                    # pass each exposure for calculating ANOVA between states
                    position_measurments.groupby("Exposure")
                    .apply(self.__calc_anova, include_groups=False)
                    .reset_index()
                )
                anovas["Position"] = i
                tukey_groups = (
                    anovas.groupby("Exposure")
                    .apply(self.__calc_tukey, include_groups=False)
                    .reset_index()
                )
                stats = pd.merge(anovas, tukey_groups, on=["Exposure", "State"])
                position_data.append(stats)
        processed_data = pd.concat(position_data).drop(columns=["ms_within"])

        return processed_data

    def __combine_means_variance_count(self, position_data_per_state):
        # receives a dataframe  with all the peptides for that state

        # calculate combined mean
        combined_mean = (
            position_data_per_state["Count"]
            * position_data_per_state["Rel. Uptake Mean"]
        ).sum() / position_data_per_state["Count"].sum()
        # calculate combined variance
        combined_within = (
            (position_data_per_state["Count"] - 1)
            * position_data_per_state["Rel. Uptake Variance"]
        ).sum()
        combined_between = (
            position_data_per_state["Count"]
            * (position_data_per_state["Rel. Uptake Mean"] - combined_mean) ** 2
        ).sum()
        denominator = (position_data_per_state["Count"] - 1).sum() + 1
        combined_variance = (combined_within + combined_between) / denominator
        # calulate combined count
        combined_count = position_data_per_state["Count"].sum()
        # return df with combined mean, combined variance and count

        return pd.Series(
            {
                "Combined Mean": combined_mean,
                "Combined Variance": combined_variance,
                "Combined Count": combined_count,
            }
        )

    def __calc_anova(self, exposure_group):
        # here exposure group contains sequence, start, end, state, MHP, MaxUptake, Center Mean, Center Variance, Count ...
        # need to return state from original exposure_group df
        means = (
            exposure_group.groupby(["State"])
            .apply(
                # change this to __combine_means_variance_count
                self.__combine_means_variance_count,
                include_groups=False,
            )
            .reset_index()
        )

        # here means contains state, combined variance, combined mean and combined count

        grand_mean = (means["Combined Mean"] * means["Combined Count"]).sum() / means[
            "Combined Count"
        ].sum()

        ss_between = (
            means["Combined Count"] * ((means["Combined Mean"] - grand_mean) ** 2)
        ).sum()
        df_between = means.shape[0] - 1
        ms_between = ss_between / df_between if df_between != 0 else 0

        ss_within = ((means["Combined Count"] - 1) * means["Combined Variance"]).sum()
        df_within = means["Combined Count"].sum() - means.shape[0]
        ms_within = ss_within / df_within if df_within != 0 else 0

        f_stat = ms_between / ms_within if ms_within != 0 else 0

        p_value = 1 - f.cdf(f_stat, df_between, df_within)

        means["ANOVA"] = p_value

        means["ms_within"] = ms_within
        means = means.set_index("State")
        return means

    def __calc_tukey(self, group):
        tukeys = pd.DataFrame()
        tukeys["State"] = group["State"]

        for state in tukeys["State"]:
            tukeys[state] = [1.0] * len(tukeys["State"])

        anova_p = group.iloc[0]["ANOVA"]
        p_threshold = 0.05
        if anova_p < p_threshold:
            ms_within = group.iloc[0]["ms_within"]
            k = len(group.index)
            n = group["Combined Count"].sum()

            for outer_index, outer_row in group.iterrows():
                for inner_index, inner_row in group.iterrows():
                    if outer_index != inner_index:
                        se = math.sqrt(
                            (ms_within / 2)
                            * (
                                1 / outer_row["Combined Count"]
                                + 1 / inner_row["Combined Count"]
                            )
                        )
                        mean_diff = abs(
                            outer_row["Combined Mean"] - inner_row["Combined Mean"]
                        )
                        q = mean_diff / se if se != 0 else 0

                        try:
                            p_tukey = psturng(q, k, n - k)
                            if isinstance(p_tukey, np.ndarray):
                                p_tukey = p_tukey[0]
                            tukeys.loc[outer_index, inner_row["State"]] = p_tukey
                        except KeyError:
                            continue

        tukeys = tukeys.set_index("State")

        return tukeys

    def get_absolute_uptake_data(self, protein, exposure, state=None):
        filtered = self.position_data.loc[
            (self.position_data["Exposure"] == exposure)
            & (self.position_data["Protein"] == protein)
        ]
        if state:
            # calc y-values
            y_values = pd.Series(
                filtered.apply(
                    lambda x: x["Combined Mean"]
                    - filtered.loc[
                        (filtered["Position"] == x["Position"])
                        & (filtered["State"] == state)
                    ].iloc[0]["Combined Mean"],
                    axis=1,
                ),
                name="Combined Mean",
            )
            # is it significant? get the passed state column
            significance = pd.Series(
                filtered.apply(lambda x: x[state], axis=1), name="p_value"
            )

            return (
                filtered[["Position", "State", "Combined Variance"]]
                .join(y_values)
                .join(significance)
            )
        else:
            return filtered[["Position", "State", "Combined Variance", "Combined Mean"]]

        return filtered[["Position", "State", "Combined Variance"]].join(y_values)

    def get_states_protein_exposure_lists(self):
        return (
            self.position_data["State"].unique().tolist(),
            self.position_data["Exposure"].unique().tolist(),
            self.position_data["Protein"].unique().tolist(),
        )


# if __name__ == "__main__":
#     model = Model("resources/csv/cluster.csv")
#     model.get_absolute_uptake_data("astex", 0.5)
