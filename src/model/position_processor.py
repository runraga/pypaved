from scipy.stats import f
from statsmodels.stats.libqsturng import psturng
import pandas as pd
import numpy as np
import multiprocessing as mp
import math


def position_iterable(positions, protein_group):
    for i in positions:
        yield i, protein_group[
            (protein_group["Start"] < i) & (protein_group["End"] >= i)
        ]


def process_protein_to_position(protein_group, progress_callback):
    min_position = protein_group["Start"].min()
    max_position = protein_group["End"].max()
    progress_callback.send(
        (f"Processing {protein_group.name}", f"{max_position-min_position} positions")
    )
    range_values = range(min_position, max_position + 1)

    iterable = position_iterable(range_values, protein_group)

    with mp.Pool() as pool:
        results = pool.map(
            process_positions,
            [(iteration, progress_callback) for iteration in iterable],
        )

    combined_df = pd.concat(results, ignore_index=True)
    
    return combined_df


def process_positions(args):
    iteration, progress_callback = args
    i, position_rows = iteration

    # progress_callback.send(("Processing position:", i))

    # at this point we have all states and exposures for all peptides covering this position
    if position_rows.shape[0] > 0:
        anovas = (
            # pass each exposure for calculating ANOVA between states
            position_rows.groupby("Exposure")
            .apply(calc_anova, include_groups=False)
            .reset_index()
        )
        anovas["Position"] = i
        tukey_groups = (
            anovas.groupby("Exposure")
            .apply(calc_tukey, include_groups=False)
            .reset_index()
        )
        stats = pd.merge(anovas, tukey_groups, on=["Exposure", "State"])
        # TODO can drop ms_within column
        return stats


def combine_means_variance_count(position_data_per_state):
    # receives a dataframe  with all the peptides for that state

    # calculate combined mean
    combined_mean = (
        position_data_per_state["Count"] * position_data_per_state["Rel. Uptake Mean"]
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


def calc_anova(exposure_group):
    # here exposure group contains sequence, start, end, state, MHP, MaxUptake, Center Mean, Center Variance, Count ...
    # need to return state from original exposure_group df
    means = (
        exposure_group.groupby(["State"])
        .apply(
            # change this to __combine_means_variance_count
            combine_means_variance_count,
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


def calc_tukey(group):
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
