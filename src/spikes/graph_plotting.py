import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    plt.legend(loc=3, bbox_to_anchor=(1, 0))
    plt.show()
    # data = data.loc[
    #     (data["State"] == 0) & (data["State"] == "protein only")
    # ].reset_index(drop=True)
    # exposure_groups = data.groupby("State")
    # print(exposure_groups)
    # exposure_groups.apply(plot_exposures, fig, ax, include_groups=True)
    # make data
    # x = data["x"]
    # y1 = data["y"] + data["std"]
    # y2 = data["y"] - data["std"]
    # y1b = data["yb"] + data["stdb"]
    # y2b = data["yb"] - data["stdb"]

    # # plot
    # fig, ax = plt.subplots()

    # ax.fill_between(x, y1, y2, alpha=0.5, linewidth=0)
    # ax.plot(x, data["y"], linewidth=2, label="a")
    # ax.fill_between(x, y1b, y2b, alpha=0.5, linewidth=0)
    # ax.plot(x, data["yb"], linewidth=2, label="b")

    # # ax.set(xlim=(0, 8), xticks=np.arange(1, 8), ylim=(0, 8), yticks=np.arange(1, 8))
