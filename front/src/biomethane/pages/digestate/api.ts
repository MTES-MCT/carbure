import { api } from "common/services/api-fetch"
import {
  BiomethaneDigestatePatchRequest,
  BiomethaneDigestateSpreading,
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
  body: BiomethaneDigestatePatchRequest
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
  body: BiomethaneDigestateSpreading
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
