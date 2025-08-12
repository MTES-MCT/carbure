import { findEntities } from "common/api"
import { api } from "common/services/api-fetch"
import { EntityType } from "common/types"
import {
  BiomethaneAmendmentAddRequest,
  BiomethaneContractPatchRequest,
  BiomethaneProductionUnitAddRequest,
  BiomethaneProductionUnitPatchRequest,
  BiomethaneDigestateStorageAddRequest,
  BiomethaneDigestateStoragePatchRequest,
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

// Production Unit API
export const getProductionUnit = async (entity_id: number) => {
  const response = await api.GET("/biomethane/production-unit/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
  return response.data
}

export const createProductionUnit = async (
  entity_id: number,
  data: BiomethaneProductionUnitAddRequest
) => {
  const response = await api.POST("/biomethane/production-unit/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}

export const updateProductionUnit = async (
  entity_id: number,
  data: BiomethaneProductionUnitPatchRequest
) => {
  const response = await api.PATCH("/biomethane/production-unit/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}

// Digestate Storage API
export const getDigestateStorages = async (entity_id: number) => {
  const response = await api.GET("/biomethane/digestate-storage/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
  return response.data
}

export const addDigestateStorage = async (
  entity_id: number,
  data: BiomethaneDigestateStorageAddRequest
) => {
  const response = await api.POST("/biomethane/digestate-storage/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}

export const updateDigestateStorage = async (
  entity_id: number,
  id: number,
  data: BiomethaneDigestateStoragePatchRequest
) => {
  const response = await api.PATCH("/biomethane/digestate-storage/{id}/", {
    params: {
      path: {
        id,
      },
      query: {
        entity_id,
      },
    },
    body: data,
  })
  return response.data
}

export const deleteDigestateStorage = async (entity_id: number, id: number) => {
  const response = await api.DELETE("/biomethane/digestate-storage/{id}/", {
    params: {
      path: {
        id,
      },
      query: {
        entity_id,
      },
    },
  })
  return response.data
}
