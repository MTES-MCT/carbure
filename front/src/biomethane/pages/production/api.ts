import { api } from "common/services/api-fetch"
import {
  BiomethaneProductionUnitPatchRequest,
  BiomethaneDigestateStorageAddRequest,
  BiomethaneDigestateStoragePatchRequest,
} from "./types"
import { toFormData } from "common/services/api"

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

export const saveProductionUnit = async (
  entity_id: number,
  data: BiomethaneProductionUnitPatchRequest
) => {
  const response = await api.PUT("/biomethane/production-unit/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: data,
    bodySerializer: (data) => toFormData(data, { excludeNulls: false }),
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
