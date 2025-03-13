"""GHG emissions utilities.

This module offers functions for:
- guessing if declared values are default values
- filter data along this property
- group and count biofuel batches according to identifiers
- plot the composed groups

A data directory used by `flag_default_values` will be expected to store the following
csv files:
- Disaggregated default values files:
  - `ddv_eec.csv`
  - `ddv_ep.csv`
  - `ddv_etd.csv`.
- Two mapping files between CarbuRe ids and the 2018/2001/EU directive:
  - `feedstock_mapping.csv`
  - `biofuel_mapping.csv`
"""

import pathlib

import pandas as pd


def flag_default_values(df: pd.DataFrame, data_dir: pathlib.Path, emission_cols: list[str]) -> pd.DataFrame:
    """Boolean DataFrame that indicate if declared emission values are default values.

    `df`'s emission values are compared to default values. All data files are should be
    accessible inside `data_dir`. See module docstring for more info about the expected
    data files.

    Args:
        df: The input DataFrame.
        data_dir: A directory containing default values and id mapping.
        emission_cols: The names of columns containing emission values.

    Returns:
        A DataFrame with bool columns flagging whether each `emission_cols` values are
        default.

    """
    ddv: dict[str, pd.DataFrame] = {}
    mappings: dict[str, pd.DataFrame] = {}
    for file_ in data_dir.iterdir():
        if file_.stem.startswith("ddv"):
            ddv[file_.stem.split("_")[1]] = pd.read_csv(file_, index_col=["biofuel", "feedstock"])
        elif file_.stem.endswith("mapping"):
            mappings[file_.stem.split("_")[0]] = pd.read_csv(file_, index_col="id")
    if not mappings or not ddv:
        raise IOError(f"Could not find required files into {data_dir.name}")

    flag_cols: dict[str, pd.Series] = {}
    candidates = df[emission_cols + ["biofuel_id", "feedstock_id"]].copy()
    candidates["feedstock"] = candidates["feedstock_id"].map(mappings["feedstock"].loc[:, "feedstock"])
    candidates["biofuel"] = candidates["biofuel_id"].map(mappings["biofuel"].loc[:, "biofuel"])
    for emission, ddv_df in ddv.items():
        candidates_ddv = candidates.join(ddv_df, on=["biofuel", "feedstock"], how="left")
        flag_cols[f"is_default_{emission}"] = (
            (candidates_ddv[emission] == candidates_ddv[f"default_value_{emission}"]).groupby("id").any()
        )

    return pd.concat(flag_cols, axis=1, join="inner")
