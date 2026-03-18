import { BiomethaneSectionId } from "./missing-fields.config"

const WAIT_FOR_ELEMENT_TIMEOUT_MS = 2000

/**
 * Waits for an element to be available in the DOM (e.g. after conditional render), then runs the resolver.
 * Uses requestAnimationFrame, then MutationObserver with a timeout.
 *
 * @param resolve - Function that returns true when the element was found and the action was performed, false to retry
 * @param options.timeoutMs - Max time to wait (default 2000)
 */
export const whenElementReady = (
  resolve: () => boolean,
  options?: { timeoutMs?: number }
) => {
  const timeoutMs = options?.timeoutMs ?? WAIT_FOR_ELEMENT_TIMEOUT_MS

  requestAnimationFrame(() => {
    if (resolve()) return

    const observer = new MutationObserver(() => {
      if (resolve()) {
        observer.disconnect()
      }
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    })

    setTimeout(() => observer.disconnect(), timeoutMs)
  })
}

/**
 * Focuses on the first available missing field from a list and scrolls it into view.
 *
 * This function handles dynamic component loading by using whenElementReady:
 * if the fields are not yet rendered, it waits for them to appear in the DOM.
 *
 * @param missingFields - An array of name attributes of form fields to focus on.
 *                        The function will focus on the first available field in the array.
 *                        If the array is empty, the function returns immediately.
 */
export const focusFirstMissingField = (missingFields: string[]) => {
  if (missingFields.length === 0) return

  whenElementReady(() => {
    const { inputs } = findMissingFieldInputs(missingFields)

    if (inputs.length > 0 && inputs[0]) {
      const firstInput = inputs[0] as HTMLElement
      firstInput.scrollIntoView({ behavior: "smooth", block: "center" })
      firstInput.focus()
      return true
    }
    return false
  })
}

const findMissingFieldInputs = (missingFields: string[]) => {
  const missingFieldsSelector = missingFields
    .map((field) => `[name="${field}"]`)
    .join(",")
  const inputs = document.querySelectorAll(missingFieldsSelector)
  const inputsByName = inputs
    .values()
    .reduce((acc: Set<string>, input: Element) => {
      const name = input.getAttribute("name") ?? ""

      if (name) {
        acc.add(name)
      }

      return acc
    }, new Set<string>())

  return { inputs, inputsByName }
}

/**
 * Scrolls the given section into view. If the section is not yet in the DOM
 * (e.g. conditionally rendered), waits for it to appear via whenElementReady.
 */
export const scrollToSection = (
  sectionId: BiomethaneSectionId,
  onSectionFound?: (element: HTMLElement) => void
) => {
  whenElementReady(() => {
    const section = document.getElementById(sectionId)
    if (section) {
      section.scrollIntoView({ behavior: "smooth", block: "center" })
      onSectionFound?.(section)
      return true
    }
    return false
  })
}
