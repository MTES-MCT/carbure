import { mockGetWithResponseData } from "common/__test__/helpers"
import { http, HttpResponse } from "msw"
import { ChargePointFilter } from "../types"
import { chargePointsList } from "./data"

export const okChargePointsList = mockGetWithResponseData(
  "/elec/charge-points/list",
  chargePointsList
)

export const okChargePointsFilters = http.get<
  any,
  { filter: ChargePointFilter }
>("/api/elec/charge-points-filters", ({ request }) => {
  const mappingFilters: Record<ChargePointFilter, string[]> = {
    [ChargePointFilter.MeasureDate]: ["2024-08", "2024-07"],
    [ChargePointFilter.ChargePointId]: [
      "Charge point id mock 1",
      "Charge point id mock 2",
    ],
    [ChargePointFilter.StationId]: ["station id 1", "station id 2"],
    [ChargePointFilter.ConcernedByReadingMeter]: ["Concerné", "Pas concerné"],
  }

  const url = new URLSearchParams(request.url)
  const currentFilter = url.get("filter") as ChargePointFilter | null
  const data = (currentFilter ? mappingFilters[currentFilter] : []) || []

  return HttpResponse.json({
    status: "success",
    data: {
      filter_values: data,
    },
  })
})
