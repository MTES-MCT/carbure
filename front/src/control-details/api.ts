import { EntityManager } from "carbure/hooks/entity"
import api, { Api } from "common-v2/services/api"
import { LotDetails } from "transaction-details/types"

const admin = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/admin/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  toggleWarning(
    entity_id: number,
    lot_id: number,
    errors: string[],
    checked: boolean
  ) {
    return api.post("/admin/lots/toggle-warning", {
      entity_id,
      lot_id,
      errors,
      checked,
    })
  },
}

const auditor = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/auditor/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  toggleWarning(
    entity_id: number,
    lot_id: number,
    errors: string[],
    checked: boolean
  ) {
    return api.post("/auditor/lots/toggle-warning", {
      entity_id,
      lot_id,
      errors,
      checked,
    })
  },
}

export default function pickApi(entity: EntityManager) {
  return entity.isAdmin ? admin : auditor
}
