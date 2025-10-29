/**
 * Focuses on the first available missing field from a list and scrolls it into view.
 *
 * This function handles dynamic component loading by using a two-step approach:
 * 1. First attempts to find and focus the field using requestAnimationFrame
 * 2. If the field is not found (component not yet rendered), uses MutationObserver
 *    to watch for DOM changes and retry when the field becomes available
 *
 * This is particularly useful when dealing with dynamically loaded sections
 * where form fields are not immediately available in the DOM.
 *
 * @param missingFields - An array of name attributes of form fields to focus on.
 *                        The function will focus on the first available field in the array.
 *                        If the array is empty, the function returns immediately.
 */
export const focusFirstMissingField = (missingFields: string[]) => {
  if (missingFields.length === 0) return

  const tryFocus = (): boolean => {
    const missingFieldsSelector = missingFields
      .map((field) => `[name="${field}"]`)
      .join(",")
    const inputs = document.querySelectorAll(missingFieldsSelector)

    if (inputs.length > 0 && inputs[0]) {
      const firstInput = inputs[0] as HTMLElement

      firstInput.scrollIntoView({ behavior: "smooth", block: "center" })
      firstInput.focus()

      return true
    }
    return false
  }

  requestAnimationFrame(() => {
    if (!tryFocus()) {
      const observer = new MutationObserver(() => {
        if (tryFocus()) {
          observer.disconnect()
        }
      })

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      })

      setTimeout(() => observer.disconnect(), 2000)
    }
  })
}
