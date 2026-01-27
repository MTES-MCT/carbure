import { api } from "common/services/api-fetch"

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const getBiomethaneProducers = (entity_id: number) =>
  api
    .GET("/biomethane/admin/producers/", {
      params: {
        query: {
          entity_id,
        },
      },
    })
    .then((res) => res.data ?? [])
