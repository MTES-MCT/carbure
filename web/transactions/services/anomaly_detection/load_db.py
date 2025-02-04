"""Load local MySQL Carbure DB in memory.

Requested tables will be loaded as DataFrames.

See the argument parser's help for usage details.
"""

import difflib
import pathlib

import connectorx as cx
import pandas as pd


def value_closest_match(targets: pd.Series, sources: pd.Series, cutoff: float = 0.8):
    """Return closest string matches of an array.

    For each element in `sources`, return the closest element found in `targets`,
    provided that there is one that is close enough wrt difflib's cutoff.

    """
    candidates = [difflib.get_close_matches(target, sources, n=1, cutoff=cutoff) for target in targets.values]
    return pd.Series([c.pop() if c else None for c in candidates], index=targets.index)


def reachable(mixed_df: pd.DataFrame, field: str):
    """Return unknown elements in mixed_df that aren't either null or empty strings."""
    return ~mixed_df[f"unknown_{field}"].isna() & (mixed_df[f"unknown_{field}"].str.strip().str.len() != 0)


def load_db(
    database_url: str,
    tables_names: pathlib.Path,
    filters: list[str],
    retrieve_unknown: list[str],
    retrieve_cutoff=0.75,
) -> dict[str, pd.DataFrame]:
    # SQL query filters. We hard code the first one in order to prevent a loading error for
    # connectorx.
    lots_query_filters = [
        "WHERE production_site_commissioning_date <= '2025-01-01'\
        AND production_site_commissioning_date > '1970-01-01'\
        AND delivery_date > '1970-01-01' \
        AND lot_status NOT IN ('DRAFT', 'DELETED')"
    ]
    #   AND delivery_date <= '2025-01-01'\
    lots_query_filters.extend(f"AND {fil}" for fil in filters)

    # Load database
    conn = database_url
    tables_names = [line[:-1] for line in open(tables_names).readlines()]

    all_tables: dict[str, pd.DataFrame] = {}
    for table in tables_names:
        query = f"SELECT * FROM {table}"
        if table == "carbure_lots":
            query = " ".join([query] + lots_query_filters)
        query += ";"
        all_tables[table] = cx.read_sql(conn, query)
        try:
            all_tables[table].set_index("id", inplace=True)
        except KeyError:
            pass

    # "Unknown" fields handling
    if retrieve_unknown:
        unknown_reachable: dict[str, pd.Series] = {}  # boolean mask
        unknown_closest_matches: dict[str, pd.Series] = {}
        unknown_reverse_mappings: dict[str, pd.Series] = {}

        sources: dict[str, pd.Series] = {
            # Sites
            "production_site": all_tables["sites"].loc[:, "name"],
            # "dispatch_site":
            "delivery_site": all_tables["sites"].loc[:, "name"],
            # Entities
            "producer": all_tables["entities"][all_tables["entities"]["entity_type"] == "Producteur"].loc[:, "name"],
            "supplier": all_tables["entities"].loc[:, "name"],
            "client": all_tables["entities"].loc[:, "name"],
        }

        assert set(retrieve_unknown) < sources.keys(), f"Input unknown fields must be inside of {sources.keys()}"

        for field in retrieve_unknown:
            unknown_reachable[field] = reachable(all_tables["carbure_lots"], field)
            unknown_closest_matches[field] = value_closest_match(
                targets=all_tables["carbure_lots"].loc[unknown_reachable[field], f"unknown_{field}"],
                sources=sources[field],
                cutoff=retrieve_cutoff,
            )
            unknown_reverse_mappings[field] = sources[field].drop_duplicates().reset_index().set_index("name").squeeze()
            retrieved = unknown_closest_matches[field].dropna()
            all_tables["carbure_lots"].loc[retrieved.index, f"carbure_{field}_id"] = retrieved.map(
                unknown_reverse_mappings[field]
            )

        # Possibly recover more production site IDs
        if "production_site" in retrieve_unknown:
            certificate_mask = (
                (~all_tables["carbure_lots"]["production_site_double_counting_certificate"].isna())
                & (all_tables["carbure_lots"]["production_site_double_counting_certificate"].str.len() != 0)
                & (all_tables["carbure_lots"]["carbure_production_site_id"].isna())
            )
            available_cert = all_tables["carbure_lots"].loc[certificate_mask, "production_site_double_counting_certificate"]
            all_tables["carbure_lots"].loc[certificate_mask, "carbure_production_site_id"] = (
                all_tables["double_counting_registrations"]
                .set_index("certificate_id")[["production_site_id"]]
                .reindex(available_cert)
                .values
            )

    return all_tables
