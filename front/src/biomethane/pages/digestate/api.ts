import { api } from "common/services/api-fetch"
import {
  BiomethaneDigestateInputRequest,
  BiomethaneDigestateSpreadingAddRequest,
} from "./types"

export const getDigestate = (
  entity_id: number,
  year: number,
  selected_entity_id?: number
) =>
  api.GET("/biomethane/digestate/", {
    params: {
      query: {
        entity_id,
        year,
        producer_id: selected_entity_id,
      },
    },
  })

export const saveDigestate = (
  entity_id: number,
  year: number,
  body: BiomethaneDigestateInputRequest
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
  body: BiomethaneDigestateSpreadingAddRequest
) =>
  api.POST("/biomethane/digestate/spreading/", {
    params: {
      query: {
        entity_id,
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
