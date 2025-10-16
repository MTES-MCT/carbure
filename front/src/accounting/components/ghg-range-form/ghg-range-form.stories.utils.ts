import { fireEvent, waitFor, within, expect } from "@storybook/test"
import { balance } from "accounting/__test__/data/balances"
import { apiTypes } from "common/services/api-fetch.types"
import { http, HttpResponse } from "msw"

export const fillGHGRangeForm = async (canvasElement: HTMLElement) => {
  const { getAllByRole, getByText } = within(canvasElement)
  const range = await waitFor(() => getAllByRole("slider"))
  const firstCursor = range[0]
  if (!firstCursor) throw new Error("First cursor not found")

  await waitFor(async () => {
    await fireEvent.change(firstCursor, { target: { value: "50" } })
    return expect(firstCursor).toHaveValue("50")
  })

  await waitFor(() => getByText("2 500 litres"))
}

export const getBalancesWithUpdatedAvailableBalance = http.get(
  "/api/tiruert/operations/balance/",
  () => {
    return HttpResponse.json<apiTypes["PaginatedBalanceResponseList"]>({
      results: [
        {
          ...balance,
          available_balance: 2500,
        },
      ],
      count: 1,
    })
  }
)
