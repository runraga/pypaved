from unittest.mock import patch
import pandas as pd
import numpy as np
import math
import os
from statsmodels.stats.libqsturng import psturng


# from src.test.test_dataframe import test_df
from src.model.process_cluster_data import (
    process_cluster,
    calculate_thompson,
    calc_summary_data,
    calc_anova,
    calc_tukey,
)

CSV_PATH = "resources/csv/cluster.csv"


def test_calc_thompson_returns_a_float():
    z = 1
    center = 1234.5678
    result = calculate_thompson(z, center)
    assert isinstance(result, float)


def test_calc_thompson_calculates_correctly():
    z = 1
    center = 5678.1234
    result = calculate_thompson(z, center)
    assert result == 5678.1234

    z = 3
    center = 945.352
    result = calculate_thompson(z, center)
    assert result == 2834.0404


def test_calc_thompson_calculates_correctly_for_dataframe():
    test_df = pd.read_csv(CSV_PATH)
    test_df_sample = test_df.loc[:1].copy()
    test_df_sample["Center_Th"] = calculate_thompson(
        test_df_sample["z"], test_df_sample["Center"]
    )
    expected_data = {
        "Center_Th": [
            2427.569136,
            2425.52587,
        ]
    }
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_series_equal(
        expected_df["Center_Th"], test_df_sample["Center_Th"]
    )


def test_get_average_std_count_returns_series():
    test_df = pd.read_csv(CSV_PATH).loc[:2]
    test_df["Center_Th"] = calculate_thompson(test_df["z"], test_df["Center"])
    result = calc_summary_data(test_df)

    assert isinstance(result, pd.Series)


def test_get_average_return_Series_with_correct_indeces():
    expected_index_names = pd.Index(["Center mean", "Center std", "Count"])

    test_df = pd.read_csv(CSV_PATH).loc[:2]
    test_df["Center_Th"] = calculate_thompson(test_df["z"], test_df["Center"])
    result = calc_summary_data(test_df)

    assert all(expected_index_names.isin(result.index))


def test_get_average_return_correct_values():
    test_df = pd.read_csv(CSV_PATH).loc[:7]
    test_df["Center_Th"] = calculate_thompson(test_df["z"], test_df["Center"])

    expected_average = np.average(test_df["Center_Th"], weights=test_df["Inten"])
    expected_variance = np.average(
        (test_df["Center_Th"] - expected_average) ** 2, weights=test_df["Inten"]
    )
    expected_std = math.sqrt(expected_variance)

    result = calc_summary_data(test_df)
    assert round(result["Center mean"], 6) == round(expected_average, 6)
    assert round(result["Center std"], 6) == round(expected_std, 6)
    assert result["Count"] == 8


def test_calc_anova_returns_correct_dataframe():
    test_df = pd.read_csv(CSV_PATH)
    test_df = test_df.loc[
        (test_df["Exposure"] == 0) & (test_df["Sequence"] == "GSSHHHHHHSSGLVPRGSHMGSV")
    ]
    test_df["Center_Th"] = calculate_thompson(test_df["z"], test_df["Center"])

    # expected p-values and msw
    expected_p_value = 0.292353
    expected_msw = 0.019433

    expected_index_names = [
        "Center mean",
        "Center std",
        "Count",
        "var",
        "ANOVA",
        "ms_within",
    ]

    result = calc_anova(test_df).reset_index()

    # data frame should have four lines
    assert result.shape[0] == 4

    # should have columns "Center mean", "Center std" "Count", "var", "ANOVA", "ms_within"
    assert expected_index_names.sort() == list(result.columns.values).sort()

    # check anova p_values and expected_msw
    assert round(result.loc[0]["ANOVA"], 6) == expected_p_value
    assert round(result.loc[0]["ms_within"], 6) == expected_msw


def test_calc_tukey_returns_correct_dataframe_when_p_value_above_0_05():
    test_df = pd.read_csv(CSV_PATH)
    test_df = test_df.loc[
        (test_df["Exposure"] == 0) & (test_df["Sequence"] == "GSSHHHHHHSSGLVPRGSHMGSV")
    ]
    test_df["Center_Th"] = calculate_thompson(test_df["z"], test_df["Center"])
    # test_df = pd.merge(test_df, calc_anova(test_df), on=["State"])
    anova_result = calc_anova(test_df).reset_index()
    tukey_result = calc_tukey(anova_result)
    assert tukey_result.eq(1).all().all()


def test_calc_tukey_returns_correct_dataframe_when_p_value_less_than_0_05():
    # setup data
    test_df = pd.read_csv(CSV_PATH)
    test_df = test_df.loc[
        (test_df["Exposure"] == 120.000008)
        & (test_df["Sequence"] == "GSSHHHHHHSSGLVPRGSHMGSV")
    ]
    test_df["Center_Th"] = calculate_thompson(test_df["z"], test_df["Center"])
    anova_result = calc_anova(test_df).reset_index()
    groups = anova_result.shape[0]
    # expected values
    # protein only to danoprevir
    danoprevir = anova_result.loc[anova_result["State"] == "danoprevir"].iloc[0]
    count_danoprevir = danoprevir["Count"]
    mean_danoprevir = danoprevir["Center mean"]

    protein_only = anova_result.loc[anova_result["State"] == "protein only"].iloc[0]
    count_protein_only = protein_only["Count"]
    mean_protein_only = protein_only["Center mean"]

    se = math.sqrt(
        (anova_result.loc[0]["ms_within"] / 2)
        * (1 / count_danoprevir + 1 / count_protein_only)
    )
    q_stat = abs(mean_danoprevir - mean_protein_only) / se
    p_tukey = psturng(q_stat, groups, anova_result["Count"].sum() - groups)

    tukey_result = calc_tukey(anova_result).reset_index()
    assert (
        tukey_result.loc[tukey_result["State"] == "protein only"].iloc[0]["danoprevir"]
        == p_tukey
    )


def test_process_cluster_returns_dataframe():
    test_df = pd.read_csv(CSV_PATH)
    test_df = test_df.loc[test_df["Sequence"] == "GSSHHHHHHSSGLVPRGSHMGSV"]
    test_df.to_csv("resources/csv/tmp_cluster.csv", index=False)

    result = process_cluster("resources/csv/tmp_cluster.csv")

    assert isinstance(result, pd.DataFrame)
    os.remove("resources/csv/tmp_cluster.csv")


def test_process_cluster_returns_():
    test_df = pd.read_csv(CSV_PATH)
    test_df = test_df.loc[test_df["Sequence"] == "GSSHHHHHHSSGLVPRGSHMGSV"]
    test_df.to_csv("resources/csv/tmp_cluster.csv", index=False)
    # actual
    result = process_cluster("resources/csv/tmp_cluster.csv")
    # expected
    expected_th = calculate_thompson(test_df["z"], test_df["Center"])
    test_df["Center_Th"] = expected_th.iloc[:]
    expected_summary = (
        test_df.groupby(["Sequence", "Exposure", "State"])
        .apply(calc_summary_data, include_groups=False)
        .reset_index()
    )
    expected_summary_merge = pd.merge(
        test_df, expected_summary, on=["Sequence", "Exposure", "State"]
    )
    expected_anova = (
        expected_summary_merge.groupby(["Exposure"])
        .apply(calc_anova, include_groups=False)
        .reset_index()
    )
    expected_tukey = (
        expected_anova.groupby(["Exposure"])
        .apply(calc_tukey, include_groups=False)
        .reset_index()
    )
    assert all(
        expected_summary.loc[:, ["Center mean", "Center std", "Count"]]
        == result.loc[:, ["Center mean", "Center std", "Count"]]
    )

    assert all(expected_anova.loc[:, "ANOVA"] == result.loc[:, "ANOVA"])
    assert all(
        expected_tukey.drop(columns=["State", "Exposure"])
        == result.loc[:, ["AT21950", "AT23551", "danoprevir", "protein only"]]
    )
    os.remove("resources/csv/tmp_cluster.csv")
