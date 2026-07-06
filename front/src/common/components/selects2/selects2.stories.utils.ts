import { userEvent, waitFor, within } from "@storybook/test"

type TextMatcher = string | RegExp

const SELECT_TIMEOUT = 3000

async function waitForSelectDropdown(
  trigger: HTMLElement
): Promise<HTMLElement> {
  return waitFor(
    async () => {
      await userEvent.click(trigger)

      const dropdown = document.querySelector<HTMLElement>("[data-dropdown]")
      if (!dropdown) {
        throw new Error("retry")
      }

      return dropdown
    },
    {
      timeout: SELECT_TIMEOUT,
      onTimeout: () => {
        return new Error("Select dropdown not found")
      },
    }
  )
}

/**
 * Opens a select (filter or form) and picks an option in the dropdown.
 */
export async function selectOption({
  trigger,
  option,
}: {
  trigger: HTMLElement
  option: TextMatcher
}) {
  const dropdown = await waitForSelectDropdown(trigger)
  const optionElement = await waitFor(() => within(dropdown).getByText(option))
  await userEvent.click(optionElement)
}

/**
 * Form select variant: finds the trigger by label
 * and then selects an option in the dropdown.
 */
export async function selectOptionByLabel({
  canvasElement,
  label,
  option,
}: {
  canvasElement: HTMLElement
  label: TextMatcher
  option: TextMatcher
}) {
  const trigger = await waitFor(() =>
    within(canvasElement).getByLabelText(label)
  )
  await selectOption({ trigger, option })
}

/**
 * Form select variant: finds the trigger by input name
 * and then selects an option in the dropdown.
 */
export async function selectOptionByName({
  canvasElement,
  name,
  option,
}: {
  canvasElement: HTMLElement
  name: string
  option: TextMatcher
}) {
  const trigger = await waitFor(() => {
    const input = canvasElement.querySelector<HTMLInputElement>(
      `input[name="${name}"]`
    )
    if (!input) {
      throw new Error(`Select trigger not found for name "${name}"`)
    }
    return input
  })

  await selectOption({ trigger, option })
}
