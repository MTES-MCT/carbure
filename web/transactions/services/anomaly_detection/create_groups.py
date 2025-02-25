import textwrap
from typing import Any

import pandas as pd


def create_groups(
    df: pd.DataFrame,
    emission_category: str,
    emission_group_cols: dict[str, list[str]],
    id_cols: list[str],
    id_names_mapping: dict[str, pd.Series],
    deduplicate: bool = True,
    n_groups_threshold: int = 10,
    n_batches_threshold: int = 40,
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
        A DataFrame with a new `group` column, assigning a group to each batch.
    """

    gb_cols = emission_group_cols.get(emission_category)
    emission_cols = [emission_category]

    df = df.loc[
        ~df[f"is_default_{emission_category}"],
        emission_cols + id_cols,
    ]

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

    grouped_df = pd.concat(label_data)
    grouped_df["group"] = grouped_df["group"].astype("category")
    grouped_df["feedstock"] = grouped_df["feedstock_id"].map(id_names_mapping["feedstock_id"])
    grouped_df["biofuel"] = grouped_df["biofuel_id"].map(id_names_mapping["biofuel_id"])
    grouped_df["country_of_origin"] = grouped_df["country_of_origin_id"].map(id_names_mapping["country_of_origin_id"])

    return grouped_df
