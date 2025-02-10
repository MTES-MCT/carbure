import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


def detect_emission_category_outliers(
    df: pd.DataFrame,
    emission_category: str,
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

    outlier_columns = ["is_lof_outlier", "is_if_outlier"]

    # Now we only keep categorical data for each type of emission
    # The idea is to have a table containing all the filters that match outlying values

    if emission_category == "eec":
        outliers = outliers[["eec", "feedstock_id"] + outlier_columns]
    elif emission_category == "ep":
        outliers = outliers[["ep", "feedstock_id", "biofuel_id"] + outlier_columns]
    elif emission_category == "etd":
        outliers = outliers[["etd", "feedstock_id"] + outlier_columns]

    return outliers


def detect_outliers(
    chosen_quantile: float,
    computed_quantiles: list[float],
    df_eec: pd.DataFrame,
    df_ep: pd.DataFrame,
    df_etd: pd.DataFrame,
) -> pd.DataFrame:
    clf_if = IsolationForest(
        **{
            "bootstrap": False,
            "contamination": "auto",
            "max_features": 1.0,
            "max_samples": "auto",
            "n_estimators": 300,
            "n_jobs": None,
            "random_state": None,
            "verbose": 0,
            "warm_start": False,
        }
    )

    clf_lof = LocalOutlierFactor(
        **{
            "algorithm": "auto",
            "contamination": "auto",
            "leaf_size": 40,
            "metric": "minkowski",
            "metric_params": None,
            "n_jobs": None,
            "n_neighbors": 30,
            "novelty": False,
            "p": 2,
        }
    )

    outliers_by_emission_category: dict[str, pd.DataFrame] = {}

    for df, emission_category in zip([df_eec, df_ep, df_etd], ["eec", "ep", "etd"]):
        outliers_by_emission_category[emission_category] = detect_emission_category_outliers(
            df,
            emission_category=emission_category,
            chosen_quantile=chosen_quantile,
            computed_quantiles=computed_quantiles,
            clf_lof=clf_lof,
            clf_if=clf_if,
        )

    return outliers_by_emission_category
