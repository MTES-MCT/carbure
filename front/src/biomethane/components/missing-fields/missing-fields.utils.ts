/**
 * Focuses on a specific form field and scrolls it into view.
 *
 * This function handles dynamic component loading by using a two-step approach:
 * 1. First attempts to find and focus the field using requestAnimationFrame
 * 2. If the field is not found (component not yet rendered), uses MutationObserver
 *    to watch for DOM changes and retry when the field becomes available
 *
 * This is particularly useful when dealing with dynamically loaded sections
 * where form fields are not immediately available in the DOM.
 *
 * @param missingField - The name attribute of the form field to focus on
 */
export const focusMissingField = (missingField?: string) => {
  if (!missingField) return

  const tryFocus = (): boolean => {
    const input = document.querySelector(
      `[name="${missingField}"]`
    ) as HTMLElement
    if (input) {
      input.scrollIntoView({ behavior: "smooth", block: "center" })

      input.focus()
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
