import numpy as np
import csv
import math
import pandas as pd


def calculate_thompson(z, center):
    f_center = center
    i_charge = z
    thompson = f_center * i_charge - ((z - 1) * 1.0078)
    return thompson


# with open("resources/csv/spike_cluster.csv", "r", encoding="utf-8") as f:
#     csvreader = csv.reader(f, delimiter=",")
#     next(csvreader, None)
#     shifts = []
#     intensities = []
#     rts = []
#     for row in csvreader:
#         shifts.append(calculate_thompson(row[11], row[-1]))
#         intensities.append(float(row[-2]))
#         rts.append(float(row[12]))


# # average is sum weighted center (in Th) / total intensity
# weighted_average = np.average(shifts, weights=intensities)
# print(weighted_average)
# wighted_variance = np.average((shifts - weighted_average) ** 2, weights=intensities)
# print(math.sqrt(wighted_variance))
# print(shifts - weighted_average)
# print(shifts)

# print(np.std(shifts))
# print(np.mean(rts))
# print(np.std(rts))

df = pd.read_csv("resources/csv/cluster.csv")
df["z"] = pd.to_numeric(df["z"])
df["Inten"] = pd.to_numeric(df["Inten"])
df["Center"] = pd.to_numeric(df["Center"])

grouped = df.groupby(["Sequence", "State", "Exposure"])
weighted = grouped.apply(
    lambda s: pd.Series(
        (
            {
                "weighted_average": np.average(
                    calculate_thompson(s["z"], s["Center"]),
                    weights=s["Inten"],
                )
            }
        )
    )
)
print(weighted)


# for name, group in grouped:
#     print(name)
