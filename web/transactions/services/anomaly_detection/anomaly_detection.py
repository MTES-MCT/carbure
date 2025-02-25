import os
import pathlib
import warnings

import pandas as pd
from django.conf import settings

warnings.filterwarnings("ignore")

DB_TABLE_NAMES = [
    "carbure_lots",
    "biocarburants",
    "double_counting_registrations",
    "entities",
    "entity_depot",
    "entity_site",
    "matieres_premieres",
    "pays",
    "production_sites_certificates",
    "production_sites_input",
    "production_sites_output",
    "sites",
]

CHOSEN_QUANTILE = 0.05
COMPUTED_QUANTILES = [0.01, 0.05, 0.10]

E_MIN, E_MAX = (0.0, 45.0)
EMISSION_COLS = ["eec", "ep", "etd", "eccr"]

EMISSION_GROUP_COLS = {
    "eec": ["feedstock_id"],
    "ep": ["feedstock_id", "biofuel_id"],
    "etd": ["feedstock_id"],
    "eccr": [],
}

CATEGORICAL_VARIABLES = [
    "biofuel_id",
    "feedstock_id",
    "carbure_producer_id",
    "carbure_production_site_id",
    "country_of_origin_id",
]

DEFAULT_IF_PARAMS = {
    "bootstrap": False,
    "contamination": 0.01,
    "max_features": 1.0,
    "max_samples": "auto",
    "n_estimators": 300,
    "n_jobs": None,
    "random_state": None,
    "verbose": 0,
    "warm_start": False,
}

DEFAULT_LOF_PARAMS = {
    "algorithm": "auto",
    "contamination": 0.01,
    "leaf_size": 40,
    "metric": "minkowski",
    "metric_params": None,
    "n_jobs": None,
    "n_neighbors": 30,
    "novelty": False,
    "p": 2,
}


def anomaly_detection(
    table_names=DB_TABLE_NAMES,
    chosen_quantile=CHOSEN_QUANTILE,
    computed_quantiles=COMPUTED_QUANTILES,
    e_min=E_MIN,
    e_max=E_MAX,
    emission_cols=EMISSION_COLS,
    emission_group_cols=EMISSION_GROUP_COLS,
    categorical_variables=CATEGORICAL_VARIABLES,
    if_params=DEFAULT_IF_PARAMS,
    lof_params=DEFAULT_LOF_PARAMS,
):
    """
    Detect outliers in lots based on their categories and GHG profile.
    Original implementation: https://gitlab.com/la-fabrique-numerique/carbure_datascience
    """

    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor

    from .create_errors import create_errors
    from .create_groups import create_groups
    from .default_values import flag_default_values
    from .detect_outliers import detect_outliers
    from .load_db import load_db

    data_dir = pathlib.Path(settings.BASE_DIR) / "transactions/services/anomaly_detection/data"

    all_tables: dict[str, pd.DataFrame] = load_db(
        database_url=os.environ["DATABASE_URL"],
        tables_names=table_names,
        filters=["delivery_date >= '2022-03-01'"],
        retrieve_unknown=["production_site", "producer"],
    )

    biocarburants = all_tables["biocarburants"]
    carbure_lots = all_tables["carbure_lots"]
    pays = all_tables["pays"]
    entities = all_tables["entities"]
    matieres_premieres = all_tables["matieres_premieres"]
    sites = all_tables["sites"]

    id_names_mapping = {
        "biofuel_id": biocarburants["name"],
        "feedstock_id": matieres_premieres["name"],
        "carbure_producer_id": entities["name"],
        "carbure_production_site_id": sites["name"],
        "country_of_origin_id": pays["name"],
    }

    carbure_lots[emission_cols] = carbure_lots[emission_cols].clip(e_min, e_max)
    ghg = carbure_lots[emission_cols + categorical_variables]
    ddv_flags = flag_default_values(ghg, data_dir, emission_cols=emission_cols)
    flagged_df = ghg.join(ddv_flags)
    flagged_df["is_default_eccr"] = False  # Add eccr for convenience, but it has no default values.

    df_ep = create_groups(flagged_df, "ep", emission_group_cols, categorical_variables, id_names_mapping)
    df_eec = create_groups(flagged_df, "eec", emission_group_cols, categorical_variables, id_names_mapping)
    df_etd = create_groups(flagged_df, "etd", emission_group_cols, categorical_variables, id_names_mapping)

    clf_if = IsolationForest(**if_params)
    clf_lof = LocalOutlierFactor(**lof_params)

    outliers_ep = detect_outliers(df_ep, "ep", emission_group_cols, chosen_quantile, computed_quantiles, clf_if, clf_lof)
    outliers_eec = detect_outliers(df_eec, "eec", emission_group_cols, chosen_quantile, computed_quantiles, clf_if, clf_lof)
    outliers_etd = detect_outliers(df_etd, "etd", emission_group_cols, chosen_quantile, computed_quantiles, clf_if, clf_lof)

    lot_ids = create_errors({"ep": outliers_ep, "eec": outliers_eec, "etd": outliers_etd})

    return lot_ids
