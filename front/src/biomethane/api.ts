import { findEntities } from "common/api"
import { api } from "common/services/api-fetch"
import { EntityType } from "common/types"
import {
  BiomethaneAmendmentAddRequest,
  BiomethaneContractAddRequest,
  BiomethaneContractPatchRequest,
} from "./types"

// TODO: Add a new entity type for buyer of biomethane
export const findBuyerBiomethaneEntities = async (query: string) =>
  findEntities(query, {
    is_enabled: true,
    entity_type: [EntityType.Producer],
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

export const createContract = async (
  entity_id: number,
  data: BiomethaneContractAddRequest
) => {
  const response = await api.POST("/biomethane/contract/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}

export const updateContract = async (
  entity_id: number,
  data: BiomethaneContractPatchRequest
) => {
  const response = await api.PATCH("/biomethane/contract/", {
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
