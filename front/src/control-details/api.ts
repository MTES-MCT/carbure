import { EntityManager } from "carbure/hooks/entity"
import api, { Api } from "common-v2/services/api"
import { LotDetails } from "lot-details/types"

const admin = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/admin/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  toggleWarning(entity_id: number, lot_id: number, errors: string[]) {
    return api.post("/admin/lots/toggle-warning", {
      entity_id,
      lot_id,
      errors,
    })
  },
}

const auditor = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/auditor/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  toggleWarning(entity_id: number, lot_id: number, errors: string[]) {
    return api.post("/auditor/lots/toggle-warning", {
      entity_id,
      lot_id,
      errors,
    })
  },
}

export default function pickApi(entity: EntityManager) {
  return entity.isAdmin ? admin : auditor
}
