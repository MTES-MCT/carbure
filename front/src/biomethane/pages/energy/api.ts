import { api } from "common/services/api-fetch"
import {
  BiomethaneEnergyInputRequest,
  BiomethaneEnergyMonthlyReportDataRequest,
} from "./types"

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
  year: number,
  body: BiomethaneEnergyInputRequest
) => {
  console.log("saveEnergy", { entity_id, year, body })
  return api.PUT("/biomethane/energy/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
    body,
  })
}

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
  year: number,
  body: BiomethaneEnergyMonthlyReportDataRequest[]
) =>
  api.PUT("/biomethane/energy/monthly-reports/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
    body,
    bodySerializer: JSON.stringify, // Body contains array of objects, our backend could not handle it in a formData
  })
