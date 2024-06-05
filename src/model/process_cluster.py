import pandas as pd


def calculate_thompson(z: int, center: float) -> float:
    f_center = center
    i_charge = z
    thompson = f_center * i_charge - ((z - 1) * 1.0078)
    return thompson


def process_cluster(path: str) -> pd.DataFrame:
    return pd.DataFrame()


def get_average_std_count(group: pd.DataFrame) -> pd.Series:
    return pd.Series()
