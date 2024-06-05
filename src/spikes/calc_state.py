""" This is a spike to look at using dataframes for calculating 
    the weighted average uptakes and std for cluseter data

    Returns:
        None: returns none but outputs a new csv file.
"""
import numpy as np
import pandas as pd


def calculate_thompson(z, center):
    f_center = center
    i_charge = z
    thompson = f_center * i_charge - ((z - 1) * 1.0078)
    return thompson


def weighted_average_std(cluster_group):

    weights = cluster_group["Inten"]
    average = np.average(cluster_group["Center_Th"], weights=weights)
    variance = np.average((cluster_group["Center_Th"] - average) ** 2, weights=weights)
    std = np.sqrt(variance)
    count = len(cluster_group)

    return pd.Series(
        {
            "Center mean": average,
            "Center std": std,
            "Count": int(count),
        }
    )

df = pd.read_csv("resources/csv/cluster.csv")
df["z"] = pd.to_numeric(df["z"])
df["Inten"] = pd.to_numeric(df["Inten"])
df["Center"] = pd.to_numeric(df["Center"])

df["Center_Th"] = calculate_thompson(df["z"], df["Center"])

grouped = df.groupby(["Sequence", "State", "Exposure"])

weighted = grouped.apply(weighted_average_std).reset_index()

additional_columns = df[
    ["Sequence", "State", "Exposure", "Start", "End", "Protein"]
].drop_duplicates()

result = pd.merge(weighted, additional_columns, on=["Sequence", "State", "Exposure"])
result = result.convert_dtypes()

# result.to_csv("resources/csv/pandas_state.csv", index=False)