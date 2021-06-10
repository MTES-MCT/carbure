import "@testing-library/jest-dom/extend-expect"
import i18n from "i18next"
import { Suspense } from "react"
import { render as baseRender } from "@testing-library/react"
import { configure } from "@testing-library/dom"
import { initReactI18next } from "react-i18next"
import { LoaderOverlay } from "common/components"
import { AppHook, useApp } from "carbure/hooks/use-app"
import { MemoryRouter, Route } from "react-router"
import { UserRightProvider } from "carbure/hooks/use-rights"

import translation from "../public/locales/fr/translation.json"
import errors from "../public/locales/fr/errors.json"
import fields from "../public/locales/fr/fields.json"

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

i18n.use(initReactI18next).init({
  resources: {
    fr: {
      translation,
      errors,
      fields,
    },
  },
  ns: ["translation", "fields", "errors"],
  defaultNS: "translation",
  supportedLngs: ["fr"],
  fallbackLng: "fr",
  lng: "fr",
  keySeparator: false,
  nsSeparator: false,
  react: {
    useSuspense: true,
  },
})

type TestRootProps = {
  url?: string
  children: React.ReactNode | ((app: AppHook) => React.ReactNode)
}

export const TestRoot = ({ url = "/org/0", children }: TestRootProps) => {
  const app = useApp()
  const element = typeof children === "function" ? children(app) : children

  return (
    <MemoryRouter initialEntries={[url]}>
      <Suspense fallback={<LoaderOverlay />}>
        <Route path="/org/:entity">
          <UserRightProvider app={app}>{element}</UserRightProvider>
        </Route>
      </Suspense>
    </MemoryRouter>
  )
}

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
