from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import get_known_certificates, get_lot_comments, get_lot_errors, get_lot_updates, get_transaction_distance
from core.models import CarbureLot, CarbureStock, Entity, UserRights
from core.serializers import CarbureLotAdminSerializer, CarbureLotReliabilityScoreSerializer, CarbureStockPublicSerializer
from transactions.repositories.audit_lots_repository import TransactionsAuditLotsRepository


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_lot_details(request, entity_id):
    lot_id = request.GET.get("lot_id", False)
    if not lot_id:
        return JsonResponse({"status": "error", "message": "Missing lot_id"}, status=400)

    auditor = Entity.objects.get(id=entity_id)
    lot = CarbureLot.objects.get(pk=lot_id)
    owner_id = str(lot.added_by_id)
    client_id = str(lot.carbure_client_id)
    supplier_id = str(lot.carbure_supplier_id)

    has_right_to_audit_owner = False
    has_right_to_audit_client = False
    has_right_to_audit_supplier = False
    if owner_id in request.session["rights"] and request.session["rights"][owner_id] == UserRights.AUDITOR:
        has_right_to_audit_client = True
    if client_id in request.session["rights"] and request.session["rights"][client_id] == UserRights.AUDITOR:
        has_right_to_audit_client = True
    if supplier_id in request.session["rights"] and request.session["rights"][supplier_id] == UserRights.AUDITOR:
        has_right_to_audit_supplier = True

    if not has_right_to_audit_client and not has_right_to_audit_supplier:
        return JsonResponse({"status": "forbidden", "message": "User not allowed"}, status=403)

    data = {}
    data["lot"] = CarbureLotAdminSerializer(lot).data
    data["parent_lot"] = CarbureLotAdminSerializer(lot.parent_lot).data if lot.parent_lot else None
    data["parent_stock"] = CarbureStockPublicSerializer(lot.parent_stock).data if lot.parent_stock else None
    data["children_lot"] = CarbureLotAdminSerializer(CarbureLot.objects.filter(parent_lot=lot), many=True).data
    data["children_stock"] = CarbureStockPublicSerializer(CarbureStock.objects.filter(parent_lot=lot), many=True).data
    data["distance"] = get_transaction_distance(lot)
    data["errors"] = get_lot_errors(lot, auditor)
    data["certificates"] = get_known_certificates(lot)
    data["updates"] = get_lot_updates(lot)
    data["comments"] = get_lot_comments(lot)
    data["control_comments"] = TransactionsAuditLotsRepository.get_auditor_lot_comments(lot)
    data["score"] = CarbureLotReliabilityScoreSerializer(lot.carburelotreliabilityscore_set.all(), many=True).data
    return JsonResponse({"status": "success", "data": data})
