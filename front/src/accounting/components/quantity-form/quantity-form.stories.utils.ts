import { userEvent, waitFor, within } from "@storybook/test"
import {
  okSimulateMinMax,
  okSimulateOperation,
} from "accounting/__test__/api/biofuels/operations"

export const fillQuantityForm = async (canvasElement: HTMLElement) => {
  const { getByRole, getAllByRole } = within(canvasElement)

  // Fill the quantity input
  const input = await waitFor(() => getByRole("spinbutton"))
  await userEvent.type(input, "1000")

  // Click on the validate button0
  const button = await waitFor(() =>
    getByRole("button", { name: "Valider la quantité" })
  )
  await userEvent.click(button)

  // Fill tC02 input
  const tC02Input = await waitFor(() => getAllByRole("spinbutton")[1])

  if (tC02Input) {
    await userEvent.type(tC02Input, "25")
  }
}

export const baseHandlers = [okSimulateMinMax, okSimulateOperation]
