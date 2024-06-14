import math
import pandas as pd
import numpy as np
from scipy.stats import f
from statsmodels.stats.libqsturng import psturng


class Model:
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.data["Center_Th"], self.data["Uptake"] = self.__calculate_uptake(
            self.data["z"], self.data["Center"], mhp=self.data["MHP"]
        )
        self.protein_groups = (
            self.data.groupby("Protein")
            .apply(self.__process_protein_to_position, include_groups=False)
            .reset_index(drop=True)
        )

    def __calculate_uptake(self, z: int, center: float, mhp: float) -> float:
        f_center = center
        i_charge = z
        thompson = f_center * i_charge - ((z - 1) * 1.0078)
        uptake = thompson - mhp ## uptake is calculated versus the zero time point not the MHP
        return thompson, uptake

    def __calc_summary_data(self, group: pd.DataFrame) -> pd.Series:
        weights = group["Inten"]
        count = len(group)

        average = np.average(group["Center_Th"], weights=weights)
        variance = np.average((group["Center_Th"] - average) ** 2, weights=weights)
        std = np.sqrt(variance)

        average_uptake = np.average(group["Uptake"], weights=weights)
        frac_uptake = average_uptake / group["MaxUptake"]
        frac_var = variance / group["MaxUptake"] ** 2
        frac_std = math.sqrt(frac_var)

        return pd.Series(
            {
                "Center mean": average,
                "Center variance": variance,
                "Center std": std,
                "Uptake mean": average_uptake,
                "Fractional uptake": frac_uptake,
                "Fractional variance": frac_var,
                "Count": int(count),
            }
        )

    def __process_protein_to_position(self, protein_group):
        max_position = protein_group["End"].max()

        position_data = []
        for i in range(1, max_position + 1):
            position_measurments = protein_group[
                (protein_group["Start"] <= i) & (protein_group["End"] >= i)
            ]
            if position_measurments.shape[0] > 0:
                anovas = (
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
        processed_data["Protein"] = protein_group.name
        return processed_data

    def __calc_anova(self, exposure_group):
        print(exposure_group.columns)
        means = exposure_group.groupby(["State"]).apply(
            self.__calc_summary_data, include_groups=False
        )
        means["var"] = means["Center std"] ** 2

        # does denominator need to multiply n-1 here?:
        grand_mean = (means["Center mean"] * means["Count"]).sum() / means[
            "Count"
        ].sum()

        ss_between = (means["Count"] * ((means["Center mean"] - grand_mean) ** 2)).sum()
        df_between = means.shape[0] - 1
        ms_between = ss_between / df_between if df_between != 0 else 0

        ss_within = (means["Count"] * means["var"]).sum()
        df_within = means["Count"].sum() - means.shape[0]
        ms_within = ss_within / df_within if df_within != 0 else 0

        f_stat = ms_between / ms_within if ms_within != 0 else 0

        p_value = 1 - f.cdf(f_stat, df_between, df_within)

        means["ANOVA"] = p_value

        means["ms_within"] = ms_within

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
            n = group["Count"].sum()

            for outer_index, outer_row in group.iterrows():
                for inner_index, inner_row in group.iterrows():
                    if outer_index != inner_index:
                        se = math.sqrt(
                            (ms_within / 2)
                            * (1 / outer_row["Count"] + 1 / inner_row["Count"])
                        )
                        mean_diff = abs(
                            outer_row["Center mean"] - inner_row["Center mean"]
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
        filtered = self.protein_groups.loc[
            (self.protein_groups["Exposure"] == exposure)
            & (self.protein_groups["Protein"] == protein)
        ]
        if state:
            # calc y-values
            y_values = pd.Series(
                filtered.apply(
                    lambda x: x["Center mean"]
                    - filtered.loc[
                        (filtered["Position"] == x["Position"])
                        & (filtered["State"] == state)
                    ].iloc[0]["Center mean"],
                    axis=1,
                ),
                name="Center mean",
            )
        else:
            y_values = pd.Series(filtered["Center mean"], name="Center mean")
        return filtered[["Position", "State", "Center std"]].join(y_values)

    def write_to_csv(self, path):
        self.protein_groups.to_csv(path)


if __name__ == "__main__":
    model = Model("resources/csv/cluster.csv")
    model.write_to_csv("resources/csv/model_data_out.csv")
