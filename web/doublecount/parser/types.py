from os import name
from typing import TypedDict


class SourcingRow(TypedDict):
    line: int
    year: int
    feedstock: str | None
    origin_country: str | None
    supply_country: str | None
    transit_country: str | None
    metric_tonnes: int


class ProductionRow(TypedDict):
    line: int
    year: int
    feedstock: str | None
    feedstock_check: str | None
    biofuel: str | None
    max_production_capacity: int
    estimated_production: int
    requested_quota: int


class ProductionBaseRow(TypedDict):
    line: int
    year: int
    feedstock: str | None
    biofuel: str | None


class RequestedQuotaRow(ProductionBaseRow):
    requested_quota: int


class ProductionForecastRow(ProductionBaseRow):
    estimated_production: int


class ProductionMaxRow(ProductionBaseRow):
    max_production_capacity: int
