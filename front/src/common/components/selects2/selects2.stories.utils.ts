import { userEvent, waitFor, within } from "@storybook/test"

type TextMatcher = string | RegExp

async function waitForSelectDropdown(): Promise<HTMLElement> {
  const dropdown = await waitFor(() => {
    const element = document.querySelector<HTMLElement>("[data-dropdown]")
    if (!element) {
      throw new Error("Select dropdown not found")
    }
    return element
  })

  return dropdown
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
  trigger.focus()
  await userEvent.keyboard("{ArrowDown}")
  const dropdown = await waitForSelectDropdown()

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
