import pandas as pd
import numpy as np
from src.model.position_processor import process_protein_to_position


# import src.controller.Controller


class Model:
    def __init__(self, path):
        # read in csv data to dataframe
        self.data = pd.read_csv(path)
        # calculated m/z of single charge
        self.summary_data = None
        self.position_data = None
        self.paved_datasets = {}

    def start_process(self, progress_callback):
        progress_callback("Processing measurements:", "Calculating MH+")
        self.data["Center MH+"] = self.__calculate_mh1plus(
            self.data["z"], self.data["Center"]
        )
        self.data["Exposure"] = self.data["Exposure"].round(2)
        # calculate mean and varaince for MH+ of all replicate measruements
        progress_callback("Processing measurements:", "calculating summary data")

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
        progress_callback("Processing measurements:", "calculating fractional update")

        self.summary_data = (
            self.summary_data.groupby(
                ["Protein", "Sequence", "Start", "End", "State", "MHP"]
            )
            .apply(self.__calc_fractional_uptakes, include_groups=False)
            .reset_index()
        )

        # calculate stats (ANOVA and Tukeyfor each protein position)
        progress_callback("Position calculations:", "processing proteins")

        self.position_data = (
            self.summary_data.groupby("Protein")
            .apply(
                process_protein_to_position,
                progress_callback,
                include_groups=False,
            )
            .reset_index()
        )
        # TODO move following code to make_datasets function
        # make datasets one for each protein
        # protein -> (non-)reference -> exposure -> data, min & max
        # one non-reference
        unique_proteins = self.position_data["Protein"].unique().tolist()
        unique_exposures = self.position_data["Exposure"].unique().tolist()
        unique_states = self.position_data["State"].unique().tolist()
        # one for each state as reference

        for protein in unique_proteins:
            self.paved_datasets[protein] = {}
            for exposure in unique_exposures:
                self.paved_datasets[protein][exposure] = {"no_ref": {}}
                no_ref_data = self.get_absolute_uptake_data(protein, exposure)
                self.paved_datasets[protein][exposure]["no_ref"]["data"] = no_ref_data
                y_max = (
                    self.position_data["Combined Mean"]
                    + self.position_data["Combined Variance"]
                ).max()
                y_min = (
                    self.position_data["Combined Mean"]
                    + self.position_data["Combined Variance"]
                ).min()
                self.paved_datasets[protein][exposure]["no_ref"]["min_max"] = (
                    y_min,
                    y_max,
                )
                ref_min = 0
                ref_max = 0
                for state in unique_states:
                    self.paved_datasets[protein][exposure][state] = {}
                    state_data = self.get_absolute_uptake_data(
                        protein, exposure, state=state
                    )
                    self.paved_datasets[protein][exposure][state]["data"] = state_data
                    y_max = (
                        state_data["Combined Mean"] + state_data["Combined Variance"]
                    ).max()
                    y_min = (
                        state_data["Combined Mean"] + state_data["Combined Variance"]
                    ).min()
                    if y_max > ref_max:
                        ref_max = y_max
                    if y_min < ref_min:
                        ref_min = y_min
                self.paved_datasets[protein]["ref_min_max"] = (ref_min, ref_max)

    def __calculate_mh1plus(self, z: int, center: float) -> float:
        f_center = center
        i_charge = z
        thompson = f_center * i_charge - ((z - 1) * 1.0078)
        return thompson

    def __calc_summary_data(self, group: pd.DataFrame) -> pd.Series:
        # self.controller.update_progress(
        #     "Processing measurements:", "Summarising replicates"
        # )

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
        # self.controller.update_progress(
        #     "Processing measurements:", "Calculating fractional uptakes"
        # )

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

    def get_states_protein_exposure_lists(self):
        return (
            self.position_data["State"].unique().tolist(),
            self.position_data["Exposure"].unique().tolist(),
            self.position_data["Protein"].unique().tolist(),
        )

    def get_dataset(self, protein, exposure, state="no_ref"):
        if state == "no_ref":
            return self.paved_datasets[protein][exposure][state]
        else:
            data = self.paved_datasets[protein][exposure][state]
            data["min_max"] = self.paved_datasets[protein]["ref_min_max"]
            return data
