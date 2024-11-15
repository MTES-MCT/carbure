from .accept_blending import AcceptBlendingMixin
from .accept_consumption import AcceptConsumptionMixin
from .accept_direct_delivery import AcceptDirectDeliveryMixin
from .accept_export import AcceptExportMixin
from .accept_in_stock import AcceptStockMixin
from .accept_processing import AcceptProcessingMixin
from .accept_rfc import AcceptRFCMixin
from .accept_trading import AcceptTradingMixin
from .cancel_accept import CancelAcceptMixin


class AcceptMixin(
    AcceptBlendingMixin,
    AcceptConsumptionMixin,
    AcceptDirectDeliveryMixin,
    AcceptExportMixin,
    AcceptStockMixin,
    AcceptProcessingMixin,
    AcceptRFCMixin,
    AcceptTradingMixin,
    CancelAcceptMixin,
):
    pass
