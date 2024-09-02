import { mockGetWithResponseData } from "carbure/__test__/helpers"
import { rest } from "msw"
import { ChargePointFilter } from "../types"
import { chargePointsList } from "./data"

export const okChargePointsList = mockGetWithResponseData(
  "/elec/charge-points/list",
  chargePointsList
)

export const okChargePointsFilters = rest.get<
  any,
  { filter: ChargePointFilter }
>("/api/elec/charge-points-filters", (req, res, ctx) => {
  const mappingFilters: Record<ChargePointFilter, (string | number)[]> = {
    [ChargePointFilter.ValidationDate]: ["2024-08", "2024-07"],
    [ChargePointFilter.ChargePointId]: [
      "Charge point id mock 1",
      "Charge point id mock 2",
    ],
    [ChargePointFilter.StationId]: ["station id 1", "station id 2"],
    [ChargePointFilter.ConcernedByReadingMeter]: ["Concerné", "Pas concerné"],
  }

  const currentFilter = req.url.searchParams.get(
    "filter"
  ) as ChargePointFilter | null
  const data = (currentFilter ? mappingFilters[currentFilter] : []) || []

  return res(
    ctx.json({
      status: "success",
      data: {
        filter_values: data,
      },
    })
  )
})
