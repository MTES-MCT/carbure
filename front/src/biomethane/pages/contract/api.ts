import { findEntities } from "common/api"
import { api } from "common/services/api-fetch"
import { EntityType } from "common/types"
import {
  BiomethaneAmendmentAddRequest,
  BiomethaneContractPatchRequest,
} from "./types"

// TODO: Add a new entity type for buyer of biomethane
export const findBuyerBiomethaneEntities = async (query: string) =>
  findEntities(query, {
    is_enabled: true,
    entity_type: [EntityType.Fournisseur_de_biom_thane],
  })

export const getContract = async (entity_id: number) => {
  const response = await api.GET("/biomethane/contract/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
  return response.data
}

export const saveContract = async (
  entity_id: number,
  data: BiomethaneContractPatchRequest
) => {
  const response = await api.PUT("/biomethane/contract/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}

export const addAmendment = async (
  entity_id: number,
  data: BiomethaneAmendmentAddRequest
) => {
  const response = await api.POST("/biomethane/contract/amendments/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}

export const getAmendment = async (entity_id: number, amendment_id: number) => {
  const response = await api.GET(`/biomethane/contract/amendments/{id}/`, {
    params: {
      path: {
        id: amendment_id,
      },
      query: {
        entity_id,
      },
    },
  })

  return response.data
}

export const getContractWatchedFields = async (entity_id: number) => {
  const response = await api.GET("/biomethane/contract/watched-fields/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
  return response.data ?? []
}
