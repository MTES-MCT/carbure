import api, { Api } from "common/services/api"

interface EntityStatsResponse {
  metabase_iframe_url: string
}

export function getEntityStats(entity_id: number) {
  return api
    .get<Api<EntityStatsResponse>>("/v5/entity/stats", {
      params: { entity_id },
    })
    .then((res) => res.data.data)
}
