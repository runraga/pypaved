import numpy as np
import pandas as pd
from scipy.stats import f
import math
from statsmodels.stats.libqsturng import psturng


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


def calc_avova(exposure_group):
    # group on state and calc weighted average
    means = exposure_group.groupby(["State"]).apply(
        weighted_average_std, include_groups=False
    )
    means["var"] = means["Center std"] ** 2

    #does denominator need to multiply n-1 here?:
    grand_mean = (means["Center mean"] * means["Count"]).sum() / means["Count"].sum()

    ss_between = (means["Count"] * ((means["Center mean"] - grand_mean) ** 2)).sum()
    df_between = means.shape[0] - 1
    ms_between = ss_between / df_between

    ss_within = (means["Count"] * means["var"]).sum()
    df_within = means["Count"].sum() - means.shape[0]
    ms_within = ss_within / df_within

    f_stat = ms_between / ms_within

    p_value = 1 - f.cdf(f_stat, df_between, df_within)

    means["ANOVA"] = p_value

    means["ms_within"] = ms_within

    return means


def calc_tukey(group):
    tukeys = pd.DataFrame()
    tukeys["State"] = group["State"]

    for state in tukeys["State"]:
        tukeys[state] = [1.0, 1.0, 1.0, 1.0]

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
                    mean_diff = abs(outer_row["Center mean"] - inner_row["Center mean"])
                    q = mean_diff / se
                    p_tukey = psturng(q, k, n - k)
                    if isinstance(p_tukey, np.ndarray):
                        p_tukey = p_tukey[0]
                    tukeys.loc[outer_index, inner_row["State"]] = p_tukey

    tukeys = tukeys.set_index("State")
    return tukeys


df = pd.read_csv("resources/csv/spike_cluster.csv")

df["Center_Th"] = calculate_thompson(df["z"], df["Center"])

anova_groups = df.groupby(["Sequence", "Exposure", "Start", "End", "Protein"])
anova_results = anova_groups.apply(calc_avova, include_groups=False).reset_index()

tukey_groups = anova_results.groupby(
    ["Sequence", "Exposure", "Start", "End", "Protein"]
)
tukey_results = tukey_groups.apply(calc_tukey, include_groups=False).reset_index()

result = pd.merge(
    anova_results,
    tukey_results,
    on=["Sequence", "Exposure", "Start", "End", "Protein", "State"],
)
result = result.drop(columns=["var", "ms_within"])
print(result)
result.to_csv("resources/csv/pandas_state_with_tukey.csv", index=False)
