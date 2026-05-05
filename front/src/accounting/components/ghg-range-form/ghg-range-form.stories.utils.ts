import { fireEvent, waitFor, within } from "@storybook/test"
import { balance } from "accounting/__test__/data/balances"
import { apiTypes } from "common/services/api-fetch.types"
import { http, HttpResponse } from "msw"

export const setGHGRangeValue = async ({
  canvasElement,
  cursorIndex,
  value,
}: {
  canvasElement: HTMLElement
  cursorIndex: number
  value: string
}) => {
  const { getAllByRole } = within(canvasElement)
  const range = await waitFor(() => getAllByRole("slider"))
  const cursor = range[cursorIndex]
  if (!cursor) throw new Error(`Cursor at index ${cursorIndex} not found`)

  await fireEvent.change(cursor, { target: { value } })
}

export const fillGHGRangeForm = async (canvasElement: HTMLElement) => {
  const { getByText } = within(canvasElement)
  await setGHGRangeValue({
    canvasElement,
    cursorIndex: 0,
    value: "50",
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
