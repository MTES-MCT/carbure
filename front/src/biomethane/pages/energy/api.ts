import { api } from "common/services/api-fetch"
import {
  BiomethaneEnergyInputRequest,
  BiomethaneEnergyMonthlyReportDataRequest,
} from "./types"

export const getYears = (entity_id: number) =>
  api.GET("/biomethane/energy/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })

export const getEnergy = (entity_id: number, year: number) =>
  api
    .GET("/biomethane/energy/", {
      params: {
        query: {
          entity_id,
          year,
        },
      },
    })
    .then((res) => res.data)

export const saveEnergy = (
  entity_id: number,
  body: BiomethaneEnergyInputRequest
) =>
  api.PUT("/biomethane/energy/", {
    params: {
      query: {
        entity_id,
      },
    },
    body,
  })

export const validateEnergy = (entity_id: number) =>
  api.POST("/biomethane/energy/validate/", {
    params: {
      query: {
        entity_id,
      },
    },
  })

export const getMonthlyReports = (entity_id: number, year: number) =>
  api
    .GET("/biomethane/energy/monthly-reports/", {
      params: {
        query: {
          entity_id,
          year,
        },
      },
    })
    .then((res) => res.data)

export const saveMonthlyReports = (
  entity_id: number,
  body: BiomethaneEnergyMonthlyReportDataRequest[]
) =>
  api.PUT("/biomethane/energy/monthly-reports/", {
    params: {
      query: {
        entity_id,
      },
    },
    body,
    bodySerializer: JSON.stringify, // Body contains array of objects, our backend could not handle it in a formData
  })
