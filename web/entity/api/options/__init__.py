from django.urls import path
from .rfc import toggle_rfc
from .trading import toggle_trading
from .stocks import toggle_stocks
from .direct_deliveries import toggle_direct_deliveries
from .unit import set_preferred_unit

urlpatterns = [
    path("rfc", toggle_rfc, name="entity-options-rfc"),
    path("trading", toggle_trading, name="entity-options-trading"),
    path("stocks", toggle_stocks, name="entity-options-stocks"),
    path("direct-deliveries", toggle_direct_deliveries, name="entity-options-direct-deliveries"),
    path("unit", set_preferred_unit, name="entity-options-unit"),
]
