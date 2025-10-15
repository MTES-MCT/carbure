import { userEvent, waitFor, within } from "@storybook/test"
import {
  fillRecipientForm,
  baseHandlers as recipientBaseHandlers,
} from "accounting/components/recipient-form/recipient-form.stories.utils"
import { okCountrySearch } from "common/__test__/api"

export const fillCountryForm = async (canvasElement: HTMLElement) => {
  const { getByPlaceholderText, getByText } = within(canvasElement)

  // Fill the country input

  // Open the autocomplete
  const input = await waitFor(() =>
    getByPlaceholderText("Rechercher un pays...")
  )
  await userEvent.click(input)
  // Type in the input
  await userEvent.type(input, "Franc")
  const option = await waitFor(() => getByText("France"))
  await userEvent.click(option)

  // Fill the recipient input
  await fillRecipientForm(canvasElement)
}

export const baseHandlers = [okCountrySearch, ...recipientBaseHandlers]
