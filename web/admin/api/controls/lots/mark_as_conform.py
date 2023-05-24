import traceback

from admin.helpers import get_admin_lots_by_status
from core.helpers import (
    filter_lots,
    filter_stock,
    get_all_stock,
    get_known_certificates,
    get_lot_comments,
    get_lot_errors,
    get_lot_updates,
    get_lots_filters_data,
    get_lots_with_metadata,
    get_stock_events,
    get_stock_filters_data,
    get_stock_with_metadata,
    get_stocks_summary_data,
    get_transaction_distance,
)
from core.decorators import is_admin
from core.models import (
    CarbureLot,
    CarbureLotComment,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
    EntityCertificate,
    GenericError,
)
from core.serializers import (
    CarbureLotAdminSerializer,
    CarbureLotCommentSerializer,
    CarbureLotPublicSerializer,
    CarbureLotReliabilityScoreSerializer,
    CarbureStockPublicSerializer,
    CarbureStockTransformationPublicSerializer,
)
from django.db.models import Case, Value, When
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F
from django.db.models.functions.comparison import Coalesce
from django.db.models.query_utils import Q
from django.http.response import JsonResponse
