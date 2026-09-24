import { balance, balanceBiofuel } from "accounting/__test__/data/balances"
import { apiTypes } from "common/services/api-fetch.types"
import { http, HttpResponse } from "msw"

export const okGetBalances = http.get(
  "/api/tiruert/operations/balance/",
  () => {
    return HttpResponse.json<apiTypes["PaginatedBalanceResponseList"]>({
      results: [balance],
      count: 1,
      total_volume: balance.available_balance,
    })
  }
)

export const okGetBalancesWithZeroAvailableBalance = http.get(
  "/api/tiruert/operations/balance/",
  () => {
    return HttpResponse.json<apiTypes["PaginatedBalanceResponseList"]>({
      results: [{ ...balance, available_balance: 0 }],
      count: 1,
      total_volume: 0,
    })
  }
)

export const okGetBalancesWithPartialRenewableShare = http.get(
  "/api/tiruert/operations/balance/",
  () => {
    return HttpResponse.json<apiTypes["PaginatedBalanceResponseList"]>({
      results: [
        {
          ...balance,
          available_balance: 250000,
          biofuel: { ...balanceBiofuel, renewable_energy_share: 0.5 },
        },
      ],
      count: 1,
      total_volume: 250000,
    })
  }
)

export const okGetBalanceFiltersDurabilityPeriod = http.get(
  "/api/tiruert/operations/balance/filters/",
  () => {
    return HttpResponse.json(["202401"])
  }
)

export const okGetBalancesWithUpdatedBoundsWhenDurabilityPeriodSelected =
  http.get("/api/tiruert/operations/balance/", ({ request }) => {
    const url = new URL(request.url)
    const hasDurabilityFilter =
      url.searchParams.getAll("durability_period").length > 0

    return HttpResponse.json<apiTypes["PaginatedBalanceResponseList"]>({
      results: [
        hasDurabilityFilter
          ? {
              ...balance,
              available_balance: 1200,
              ghg_reduction_min: 62.34,
              ghg_reduction_max: 78.91,
            }
          : balance,
      ],
      count: 1,
      total_volume: 1200,
    })
  })
