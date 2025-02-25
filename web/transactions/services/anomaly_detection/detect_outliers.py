import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


def detect_outliers(
    df: pd.DataFrame,
    emission_category: str,
    emission_group_cols: dict[str, list[str]],
    chosen_quantile: float,
    computed_quantiles: list[float],
    clf_lof: IsolationForest,
    clf_if: LocalOutlierFactor,
) -> pd.DataFrame:
    outliers = pd.DataFrame(columns=df.columns.tolist() + ["is_lof_outlier", "is_if_outlier"])

    for key, group in df.groupby("group", observed=True):
        if key == "Autres":
            continue

        group_quantiles = group[emission_category].quantile(computed_quantiles)
        chosen_quantile_emissions: float = group_quantiles.loc[chosen_quantile]

        group["is_lof_outlier"] = clf_lof.fit_predict(group[[emission_category]]) == -1
        group["is_if_outlier"] = clf_if.fit_predict(group[[emission_category]]) == -1

        group_outliers = group[
            (group["is_lof_outlier"] | group["is_if_outlier"]) & (group[emission_category] < chosen_quantile_emissions)
        ]

        outliers = pd.concat([outliers, group_outliers], axis=0)

    # Now we only keep categorical data for each type of emission
    # The idea is to have a frame containing all the filters that match outlying values
    outlier_columns = ["is_lof_outlier", "is_if_outlier"]
    if emission_category in emission_group_cols:
        cols = [emission_category] + emission_group_cols[emission_category] + outlier_columns
        outliers = outliers[cols]

    return outliers
