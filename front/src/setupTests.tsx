import "@testing-library/jest-dom/extend-expect"
import i18n from "i18next"
import { Suspense } from "react"
import { render as baseRender } from "@testing-library/react"
import { configure } from "@testing-library/dom"
import { I18nextProvider, initReactI18next } from "react-i18next"
import Backend from "i18next-http-backend"
import { LoaderOverlay } from "common/components"

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

i18n
  .use(Backend)
  .use(initReactI18next)
  .init({
    ns: ["translations", "fields", "errors"],
    defaultNS: "translations",
    supportedLngs: ["fr"],
    fallbackLng: "fr",
    lng: "fr",
    keySeparator: false,
    nsSeparator: false,
    react: {
      useSuspense: true,
    },
    backend: {
      loadPath: "/v2/locales/{{lng}}/{{ns}}.json",
    },
  })

export function render(element: any) {
  const root = document.createElement("div")
  root.setAttribute("id", "root")
  document.body.append(root)

  const jsx = (
    <I18nextProvider i18n={i18n}>
      <Suspense fallback={<LoaderOverlay />}>{element}</Suspense>
    </I18nextProvider>
  )

  return baseRender(jsx, { container: root })
}

beforeEach(() => {
  modal.textContent = ""
  dropdown.textContent = ""
  notifications.textContent = ""
})
