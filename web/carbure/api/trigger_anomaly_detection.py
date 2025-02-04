from core.utils import CarbureEnv
from transactions.services.anomaly_detection import anomaly_detection


def trigger_anomaly_detection(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_staff:
        raise Exception("Unauthorized")

    lot_ids = anomaly_detection()
    return [{"lot_url": f"{CarbureEnv.get_base_url()}/org/9/controls/2025/lots#lot/{lot_id}"} for lot_id in lot_ids]
