import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as Line2D
from src.model.process_cluster_data import Model


def plot_exposures(exposure_group):
    # fig.suptitle(exposure_group.iloc[0]["Exposure"])
    # for index, row in exposure_group.iterrows():
    p_threshold = 0.05
    state = exposure_group.name
    full_positions = pd.Series(
        range(1, exposure_group["Position"].max() + 1), name="Position"
    )

    exposure_group = pd.merge(full_positions, exposure_group, on="Position", how="left")
    plt.plot(
        exposure_group["Position"],
        exposure_group["Combined Mean"],
        linewidth=2,
        label=state,
    )

    def check_significance(row):
        # try:
        if row["p_value"] < 0.05:
            return row["Combined Mean"] + 0.0025
        # except TypeError:
        else:
            return np.NaN

    # exposure_group["is_significant"] = pd.Series(
    #     [pd.NA] * len(exposure_group), dtype="Float64"
    # )
    exposure_group["is_significant"] = exposure_group.apply(check_significance, axis=1)
    print("updated:", exposure_group["is_significant"])
    plt.plot(
        exposure_group["Position"],
        exposure_group["is_significant"],
        ".k",
        linewidth=2,
        markersize=1,
    )
    plt.fill_between(
        exposure_group["Position"],
        exposure_group["Combined Mean"] - np.sqrt(exposure_group["Combined Variance"]),
        exposure_group["Combined Mean"] + np.sqrt(exposure_group["Combined Variance"]),
        alpha=0.10,
        linewidth=0.5,
    )

    return


if __name__ == "__main__":
    model = Model("resources/csv/cluster.csv")
    data = model.get_absolute_uptake_data("astex", 0.5, state="danoprevir")
    data.groupby("State").apply(plot_exposures, include_groups=False)
    plt.scatter(
        [], [], color="black", label="Significant difference to control", marker="."
    )
    plt.legend(loc=3, bbox_to_anchor=(1, 0))
    plt.show()

