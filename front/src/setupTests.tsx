import "@testing-library/jest-dom/extend-expect"
import i18n from "i18next"
import { Suspense } from "react"
import { render as baseRender } from "@testing-library/react"
import { configure } from "@testing-library/dom"
import { initReactI18next } from "react-i18next"
import { LoaderOverlay } from "common/components/scaffold"
import { MemoryRouter, Routes } from "react-router"

import translation from "../public/locales/fr/translation.json"
import errors from "../public/locales/fr/errors.json"
import fields from "../public/locales/fr/fields.json"
import feedstocks from "../public/locales/fr/feedstocks.json"
import biofuels from "../public/locales/fr/biofuels.json"
import countries from "../public/locales/fr/countries.json"
import useUserManager, { UserContext } from "carbure/hooks/user"
import { EntityContext, useEntityManager } from "carbure/hooks/entity"
import { PortalProvider } from "common/components/portal"

configure({
  getElementError(message) {
    const error = new Error(message ?? "Error")
    error.name = "TestingLibraryElementError"
    return error
  },
})

// mock window.open (jsdom does not implement it)
window.open = jest.fn()

// mock scrollIntoView method
Element.prototype.scrollIntoView = jest.fn()

jest.setTimeout(30000)

i18n.use(initReactI18next).init({
  resources: {
    fr: {
      translation,
      errors,
      fields,
      feedstocks,
      biofuels,
      countries,
    },
  },
  ns: [
    "translation",
    "fields",
    "errors",
    "feedstocks",
    "biofuels",
    "countries",
  ],
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

type RootProps = {
  url?: string
  children: React.ReactNode
}

export const TestRoot = ({ url, children }: RootProps) => (
  <MemoryRouter initialEntries={[url ?? "/"]}>
    <Suspense fallback={<LoaderOverlay />}>
      <App>{children}</App>
    </Suspense>
  </MemoryRouter>
)

const App = ({ children }: RootProps) => {
  const user = useUserManager()
  const entity = useEntityManager(user)

  return (
    <UserContext.Provider value={user}>
      <EntityContext.Provider value={entity}>
        <PortalProvider>
          <Routes>{children}</Routes>
          {user.loading && <LoaderOverlay />}
        </PortalProvider>
      </EntityContext.Provider>
    </UserContext.Provider>
  )
}

export function render(element: any) {
  const root = document.createElement("div")
  root.setAttribute("id", "root")
  document.body.append(root)
  return baseRender(element, { container: root })
}
