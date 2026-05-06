import { userEvent, waitFor, within } from "@storybook/test"
import { setGHGRangeValue } from "accounting/components/ghg-range-form/ghg-range-form.stories.utils"

export const clickNextStepButton = async (canvasElement: HTMLElement) => {
  const { getByRole } = within(canvasElement)
  const nextStepButton = await waitFor(() =>
    getByRole("button", { name: "Suivant" })
  )
  await userEvent.click(nextStepButton)
}

export const selectBiofuel = async (canvasElement: HTMLElement) => {
  const { getByPlaceholderText, getByText } = within(canvasElement)
  const input = await waitFor(() => getByPlaceholderText("Ex: EMHV"))

  await userEvent.click(input)
  await userEvent.type(input, "ETH")

  const option = await waitFor(() => getByText("ETH"))
  await userEvent.click(option)
}

export const fillBiofuelFiltersStep = async (canvasElement: HTMLElement) => {
  await selectBiofuel(canvasElement)
  await setGHGRangeValue({
    canvasElement,
    cursorIndex: 0,
    value: "50",
  })
}
