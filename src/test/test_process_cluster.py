import pytest
import pandas as pd
from src.model.process_cluster import (
    process_cluster,
    calculate_thompson,
    get_average_std_count,
)

CSV_PATH = "resources/csv/cluster.csv"

TEST_DATA = {
    "Inten": [
        89292,
        2394778,
    ],
    "Center": [
        607.648134,
        485.911414,
    ],
    "z": [
        4,
        5,
    ],
}


def test_return_dataframe():

    result = process_cluster(CSV_PATH)
    assert isinstance(result, pd.DataFrame)


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
    df = pd.DataFrame(TEST_DATA)
    df["Center_Th"] = calculate_thompson(df["z"], df["Center"])
    expected_data = {
        "Center_Th": [
            2427.569136,
            2425.52587,
        ]
    }
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_series_equal(expected_df["Center_Th"] , df["Center_Th"])


def test_get_average_std_count_returns_series():
    df = pd.DataFrame()
    result = get_average_std_count(df)
    assert isinstance(result, pd.Series)




