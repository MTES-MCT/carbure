import { userEvent, waitFor, within } from "@storybook/test"

export const fillRecipientForm = async (canvasElement: HTMLElement) => {
  const { getByRole, getByText } = within(canvasElement)

  // Open the autocomplete
  const input = await waitFor(() => getByRole("textbox"))
  await userEvent.click(input)

  // Type in the input
  await userEvent.type(input, "Test")

  // Wait for the option to appear and click on it
  const option = await waitFor(() => getByText("Opérateur Test"))
  await userEvent.click(option)
}
