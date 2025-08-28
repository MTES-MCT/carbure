import { api } from "common/services/api-fetch"
import {
  BiomethaneDigestateAddRequest,
  BiomethaneDigestateSpreadingAddRequest,
} from "./types"

export const getYears = (entity_id: number) =>
  api.GET("/biomethane/digestate/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })

export const getDigestate = (entity_id: number, year: number) =>
  api.GET("/biomethane/digestate/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
  })

export const saveDigestate = (
  entity_id: number,
  year: number,
  body: BiomethaneDigestateAddRequest
) =>
  api.PUT("/biomethane/digestate/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
    body,
  })

export const addSpreadingDepartment = (
  entity_id: number,
  year: number,
  body: BiomethaneDigestateSpreadingAddRequest
) =>
  api.POST("/biomethane/digestate/spreading/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
    body,
  })

export const deleteSpreadingDepartment = (
  entity_id: number,
  spreading_id: number
) =>
  api.DELETE("/biomethane/digestate/spreading/{id}/", {
    params: {
      query: {
        entity_id,
      },
      path: {
        id: spreading_id,
      },
    },
  })

export const validateDigestate = (entity_id: number) =>
  api.POST("/biomethane/digestate/validate/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
