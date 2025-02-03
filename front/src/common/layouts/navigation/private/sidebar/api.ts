import { api as apiFetch } from "common/services/api-fetch"

export const getNavStats = (entity_id: number) => {
  return apiFetch.GET(`/nav-stats`, {
    params: {
      query: {
        entity_id,
      },
    },
  })
}
