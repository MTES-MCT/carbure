import { api } from "common/services/api-fetch"

export function getYears(entity_id: number) {
  return api.GET("/elec-v2/certificates/years/", {
    params: { query: { entity_id } },
  })
}
