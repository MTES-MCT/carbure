from django.urls import path
from .release_for_consumption import toggle_release_for_consumption
from .trading import toggle_trading
from .stocks import toggle_stocks
from .direct_deliveries import toggle_direct_deliveries
from .unit import set_preferred_unit

urlpatterns = [
    path("release-for-consumption", toggle_release_for_consumption, name="entity-options-release-for-consumption"),
    path("trading", toggle_trading, name="entity-options-trading"),
    path("stocks", toggle_stocks, name="entity-options-stocks"),
    path("direct-deliveries", toggle_direct_deliveries, name="entity-options-direct-deliveries"),
    path("unit", set_preferred_unit, name="entity-options-unit"),
]
