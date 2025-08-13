import { api } from "common/services/api-fetch"
import {
  BiomethaneInjectionSiteAddRequest,
  BiomethaneInjectionSiteUpdateRequest,
} from "./types"

export const getInjectionSite = async (entity_id: number) => {
  const response = await api.GET("/biomethane/injection-site/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
  return response.data
}

export const createInjectionSite = async (
  entity_id: number,
  data: BiomethaneInjectionSiteAddRequest
) => {
  const response = await api.POST("/biomethane/injection-site/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}

export const updateInjectionSite = async (
  entity_id: number,
  data: BiomethaneInjectionSiteUpdateRequest
) => {
  const response = await api.PUT("/biomethane/injection-site/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}
