import { userEvent, waitFor, within } from "storybook/test"

export const fillFromDepotForm = async (canvasElement: HTMLElement) => {
  const { getByRole, getByText } = within(canvasElement)

  // Open the autocomplete
  const input = await waitFor(() => getByRole("textbox"))
  await userEvent.click(input)

  // Type in the input
  await userEvent.type(input, "Test")

  // Wait for the option to appear and click on it
  const option = await waitFor(() => getByText("Test Delivery Site"))
  await userEvent.click(option)
}
