import { EntityManager } from "carbure/hooks/entity"
import api, { Api } from "common-v2/services/api"
import { LotDetails } from "lot-details/types"

const admin = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/admin/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  toggleWarning(entity_id: number, lot_id: number, error: string) {
    return api.post("/admin/lots/toggle-warning", {
      entity_id,
      lot_id,
      error,
    })
  },
}

const auditor = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/auditor/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  toggleWarning(entity_id: number, lot_id: number, error: string) {
    return api.post("/auditor/lots/toggle-warning", {
      entity_id,
      lot_id,
      error,
    })
  },
}

export default function pickApi(entity: EntityManager) {
  if (entity.isAdmin) return admin
  else if (entity.isAuditor) return auditor
  else throw new Error("Entity is not allowed to do controls")
}
