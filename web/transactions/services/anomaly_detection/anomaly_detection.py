import os
import pathlib
import warnings

import pandas as pd
from django.conf import settings

warnings.filterwarnings("ignore")

CHOSEN_QUANTILE = 0.05
COMPUTED_QUANTILES = [0.01, 0.05, 0.10]

E_MIN, E_MAX = (0.0, 45.0)
EMISSION_COLS = ["eec", "ep", "etd", "eccr"]


def anomaly_detection():
    from .create_errors import create_errors
    from .create_groups import create_eec_groups, create_ep_groups, create_etd_groups
    from .default_values import flag_default_values
    from .detect_outliers import detect_outliers
    from .load_db import load_db

    data_dir = pathlib.Path(settings.BASE_DIR) / "transactions/services/anomaly_detection/data"
    tables_names_path = data_dir / "db_tables_names.txt"

    all_tables: dict[str, pd.DataFrame] = load_db(
        database_url=os.environ["DATABASE_URL"],
        tables_names=tables_names_path,
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

    categorical_variables = list(id_names_mapping)

    carbure_lots[EMISSION_COLS] = carbure_lots[EMISSION_COLS].clip(E_MIN, E_MAX)
    ghg = carbure_lots[EMISSION_COLS + categorical_variables]
    ddv_flags = flag_default_values(ghg, data_dir, emission_cols=EMISSION_COLS)
    flagged_df = ghg.join(ddv_flags)
    flagged_df["is_default_eccr"] = False  # Add eccr for convenience, but it has no default values.

    df_eec = create_eec_groups(flagged_df, categorical_variables, id_names_mapping)
    df_ep = create_ep_groups(flagged_df, categorical_variables, id_names_mapping)
    df_etd = create_etd_groups(flagged_df, categorical_variables, id_names_mapping)

    outliers_by_emission_category = detect_outliers(
        CHOSEN_QUANTILE,
        COMPUTED_QUANTILES,
        df_eec=df_eec,
        df_ep=df_ep,
        df_etd=df_etd,
    )

    create_errors(outliers_by_emission_category)
