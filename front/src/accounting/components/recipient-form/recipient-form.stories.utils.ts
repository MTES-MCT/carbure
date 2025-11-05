import { userEvent, waitFor, within } from "@storybook/test"
import { okFindEligibleTiruertEntities } from "./__test__/api"

export const fillRecipientForm = async (canvasElement: HTMLElement) => {
  const { getByPlaceholderText, getByText } = within(canvasElement)

  // Open the autocomplete
  const input = await waitFor(() =>
    getByPlaceholderText("Rechercher un destinataire")
  )
  await userEvent.click(input)

  // Type in the input
  await userEvent.type(input, "Test")

  // Wait for the option to appear and click on it
  const option = await waitFor(() => getByText("Opérateur Test"))
  await userEvent.click(option)
}

export const baseHandlers = [okFindEligibleTiruertEntities]
