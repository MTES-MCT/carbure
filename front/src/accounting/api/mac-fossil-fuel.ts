import { api, getDownloadUrl } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"

export const downloadMacFossilFuel = (entity_id: number, year: number) =>
  getDownloadUrl("/tiruert/mac-fossil-fuel/export/", { entity_id, year })

export type MacFossilFuel = {
  fuel: string
  volume: number
  year: number
  month: number
}

export const getMacFossilFuels = async (
  entity_id: number,
  year: number
): Promise<MacFossilFuel[]> => {
  return api
    .GET("/tiruert/mac-fossil-fuel/", {
      params: {
        query: {
          entity_id: `${entity_id}`,
          year,
          page_size: 1000,
        },
      },
    })
    .then(
      (res) =>
        res.data?.results.map((mac) => ({
          fuel: mac.fuel,
          volume: mac.volume ?? 0,
          year: mac.year,
          month: mac.period % 100,
        })) ?? []
    )
}

export const replaceMacFossilFuels = async (
  entity_id: number,
  year: number,
  macs: apiTypes["MacFossilFuelInputRequest"][]
) => {
  return api.PUT("/tiruert/mac-fossil-fuel/replace/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
    body: macs,
    bodySerializer: JSON.stringify,
  })
}
