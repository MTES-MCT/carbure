import { userEvent, waitFor, within } from "storybook/test"
import {
  okSimulateMinMax,
  okSimulateOperation,
} from "accounting/__test__/api/biofuels/operations"

export const fillQuantityInput = async (
  canvasElement: HTMLElement,
  quantity: string
) => {
  const { getByRole } = within(canvasElement)
  const input = await waitFor(() => getByRole("spinbutton"))

  return userEvent.type(input, quantity)
}

export const fillQuantityForm = async (
  canvasElement: HTMLElement,
  options: { quantity?: string; tC02?: string | null } = {}
) => {
  const defaultOptions = {
    quantity: "1000",
    tC02: "25",
  }
  const { quantity, tC02 } = { ...defaultOptions, ...options }

  const { getByRole, getAllByRole, getByText } = within(canvasElement)

  // Fill the quantity input
  await fillQuantityInput(canvasElement, quantity)

  // Click on the validate button
  const button = await waitFor(() =>
    getByRole("button", { name: "Valider la quantité" })
  )
  await userEvent.click(button)

  // Await the tCO2 input label is visible
  await waitFor(() => getByText("Saisir un montant en tCO2 évitées *"))
  const tC02Input = await waitFor(() => getAllByRole("spinbutton")[1])

  // Fill tC02 input if it is not null
  if (tC02Input && tC02) {
    await userEvent.type(tC02Input, tC02)
  }
}

export const baseHandlers = [okSimulateMinMax, okSimulateOperation]
