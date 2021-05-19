import "@testing-library/jest-dom/extend-expect"
import { render as baseRender } from "@testing-library/react"
import { configure } from "@testing-library/dom"

configure({
  getElementError(message) {
    const error = new Error(message ?? "Error")
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

// mock window.open (jsdom does not implement it)
window.open = jest.fn()

jest.setTimeout(10000)

jest.mock("react-i18next", () => ({
  // this mock makes sure any components using the translate hook can use it without a warning being shown
  useTranslation: () => {
    return {
      t: (str: string) => str,
      i18n: {
        changeLanguage: () => new Promise(() => {}),
      },
    }
  },
  Trans: ({ children }: any) => children,
}))

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
