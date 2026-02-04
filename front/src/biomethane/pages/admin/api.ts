import { api } from "common/services/api-fetch"

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

export const createDeclaration = (
  year: number,
  entity_id: number,
  selected_entity_id?: number
) =>
  api.POST("/biomethane/annual-declaration/", {
    params: {
      query: {
        entity_id,
        year,
        producer_id: selected_entity_id,
      },
    },
    body: {
      producer: selected_entity_id!,
      year,
      is_open: true,
    },
  })
