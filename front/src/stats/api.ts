import api, { Api } from "common/services/api"


interface EntityStatsResponse {
  metabase_iframe_url: string
}

export function getEntityStats(entity_id: number) {
  return api.get<Api<EntityStatsResponse>>(
    "/v5/stats/entity",
    {
      params: { entity_id },
    }
  ).then(res => {
    console.log(res)
    return res.data.data
  })
}
