from datetime import date
from decimal import Decimal

from h2.handlers import H2ActionHandler
from traceability.tests.excel import fill_action_template


def filled_h2_template(
    *,
    pos_id,
    material_name,
    site_name,
    certificate_id="",
    lot_id="LOT-001",
    lot_quantity=Decimal("314"),
    producer="Air Liquide",
    shipping_date=date(2026, 1, 15),
    shipping_distance=25,
    shipping_method="Transport routier",
    shipping_fuel_type="Diesel B7",
    working_date=date(2026, 2, 1),
    etd1=Decimal("1.250"),
    etd2=Decimal("0.750"),
    consumed_on_production_site="Non",
    extra_headers=None,
):
    return fill_action_template(
        H2ActionHandler(),
        {
            "lot_id": lot_id,
            "lot_quantity": lot_quantity,
            "producer": producer,
            "consumed_on_production_site": consumed_on_production_site,
            "pos_id": pos_id,
            "material": material_name,
            "certificate": certificate_id,
            "quantity": Decimal("120000.000"),
            "site": site_name,
            "shipping_date": shipping_date,
            "shipping_distance": shipping_distance,
            "shipping_method": shipping_method,
            "shipping_fuel_type": shipping_fuel_type,
            "working_date": working_date,
            "ei": 0,
            "ep": 0,
            "etd1": etd1,
            "etd2": etd2,
            "eu": 0,
            "eccs": 0,
        },
        extra_headers=extra_headers,
    )
