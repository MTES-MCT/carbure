import textwrap
from typing import Any

import pandas as pd


def create_groups(
    df: pd.DataFrame,
    gb_cols: list[str],
    id_cols: list[str],
    emission_cols: list[str],
    id_names_mapping: dict[str, pd.Series],
    deduplicate: bool = True,
    n_groups_threshold: int = 10,
    n_batches_threshold: int = 50,
) -> pd.DataFrame:
    # deduplicate = False
    """Create a new "group" column to prepare plotting.

    Groups are constituted using a groupby on `gb_cols` values. Groups that have too few
    batches, or too few unique sets of keys picked from `id_cols` will be gathered into
    a single group named "Autres". `n_groups_threshold` and `n_batches_threshold`
    control this behavior. `gb_cols` should always be a subset of `id_cols`, which holds
    all available identifiers.

    Args:
        df: The input DataFrame
        gb_cols: The columns to group by.
        id_cols: The columns containing all of the available identifiers.
        emission_cols: The studied emission columns (it can be a list of a single
          element)
        id_names_mapping: A mapping of pandas Series associating identifiers
          (integers) to their names.
        deduplicate: If True, only keep a single sample for equal given combinations of
          identifiers + emission value.
        n_groups_threshold: If the size of a group, as grouped by `gb_cols` is under
          this threshold, it is discarded.
        n_batches_threshold: It the number of (potentially deduplicated) samples inside
          a group is below this threshold, it is discarded.

    Returns:
        A DataGrame with a new `group` column, assigning a group to each batch.
    """
    if not set(gb_cols).issubset(df.columns):
        raise ValueError("gb_cols must be a subset of the DataFrame's columns")
    if df.empty:
        return pd.concat([df, pd.DataFrame(columns=["group"])], axis=1)

    filtered_df = df.dropna(subset=gb_cols)
    n_groups = filtered_df.drop_duplicates(subset=id_cols).groupby(gb_cols).size()
    if deduplicate:
        filtered_df.drop_duplicates(subset=id_cols + emission_cols, inplace=True)
    grouped = filtered_df.groupby(gb_cols)

    small_groups: list[pd.DataFrame] = []
    split_data: list[tuple[Any, pd.DataFrame]] = []
    for group_key, group_data in grouped:
        if len(group_data) < n_batches_threshold or n_groups.loc[group_key] < n_groups_threshold:
            small_groups.append(group_data)
        else:
            split_data.append((group_key, group_data))
    if small_groups:
        small_group_data = pd.concat(small_groups)
        split_data.append(("Autres", small_group_data))

    # Prepare filtered data for plotting
    label_data = []
    for group_key, group_data in split_data:
        label_parts = [
            "\n".join(textwrap.wrap(id_names_mapping[col].loc[val][:50], 25))
            for col, val in zip(gb_cols, group_key)
            if group_key != "Autres"
        ]
        label = "Autres" if group_key == "Autres" else ", ".join(label_parts)
        group_data["group"] = label
        label_data.append(group_data)
    return pd.concat(label_data)


def create_eec_groups(flagged_df: pd.DataFrame, categorical_variables: list[str], id_names_mapping: dict[str, str]):
    df_eec = create_groups(
        flagged_df.loc[
            ~flagged_df["is_default_eec"],
            ["eec"] + categorical_variables,
        ],
        gb_cols=["feedstock_id"],
        id_cols=categorical_variables,
        emission_cols=["eec"],
        id_names_mapping=id_names_mapping,
        n_groups_threshold=10,
        n_batches_threshold=40,
        deduplicate=True,
    )

    df_eec["group"] = df_eec["group"].astype("category")
    df_eec["feedstock"] = df_eec["feedstock_id"].map(id_names_mapping["feedstock_id"])

    return df_eec


def create_ep_groups(flagged_df: pd.DataFrame, categorical_variables: list[str], id_names_mapping: dict[str, str]):
    df_ep = create_groups(
        flagged_df.loc[
            ~flagged_df["is_default_ep"],
            ["ep"] + categorical_variables,
        ],
        gb_cols=["feedstock_id", "biofuel_id"],
        id_cols=categorical_variables,
        emission_cols=["ep"],
        id_names_mapping=id_names_mapping,
        n_groups_threshold=10,
        n_batches_threshold=40,
        deduplicate=True,
    )
    df_ep["group"] = df_ep["group"].astype("category")
    df_ep["feedstock"] = df_ep["feedstock_id"].map(id_names_mapping["feedstock_id"])
    df_ep["biofuel"] = df_ep["biofuel_id"].map(id_names_mapping["biofuel_id"])

    return df_ep


def create_etd_groups(flagged_df: pd.DataFrame, categorical_variables: list[str], id_names_mapping: dict[str, str]):
    df_etd = create_groups(
        flagged_df.loc[
            ~flagged_df["is_default_etd"],
            ["etd"] + categorical_variables,
        ],
        gb_cols=["feedstock_id"],
        id_cols=categorical_variables,
        emission_cols=["etd"],
        id_names_mapping=id_names_mapping,
        n_groups_threshold=10,
        n_batches_threshold=40,
        deduplicate=True,
    )

    df_etd["group"] = df_etd["group"].astype("category")
    df_etd["feedstock"] = df_etd["feedstock_id"].map(id_names_mapping["feedstock_id"])
    df_etd["biofuel"] = df_etd["biofuel_id"].map(id_names_mapping["biofuel_id"])
    df_etd["country_of_origin"] = df_etd["country_of_origin_id"].map(id_names_mapping["country_of_origin_id"])

    return df_etd
