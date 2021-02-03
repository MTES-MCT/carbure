import "@testing-library/jest-dom/extend-expect"
import { render as baseRender } from "@testing-library/react"
import { configure } from "@testing-library/dom"

configure({
  testIdAttribute: "data-my-test-id",
  getElementError(message, container) {
    const error = new Error(message)
    error.name = "TestingLibraryElementError"
    return error
  },
})

const modal = document.createElement("div")
modal.setAttribute("id", "modal")

const dropdown = document.createElement("div")
dropdown.setAttribute("id", "dropdown")

const notifications = document.createElement("div")
notifications.setAttribute("id", "notifications")

document.body.append(modal, dropdown, notifications)

export function render(element: any) {
  const root = document.createElement("div")
  root.setAttribute("id", "root")
  document.body.append(root)
  return baseRender(element, { container: root })
}

beforeEach(() => {
  modal.textContent = ""
  dropdown.textContent = ""
  notifications.textContent = ""
})
