import { Api } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"

interface EntityStatsResponse {
  metabase_iframe_url: string
}

export function getEntityStats(entity_id: number) {
  return apiFetch
    .GET("/entities/stats/", {
      params: { query: { entity_id } },
    })
    .then((res) => res.data)
}
