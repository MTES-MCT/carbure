import React, { Suspense, useEffect } from "react"
import type { Preview } from "@storybook/react"
import i18n from "../src/i18n"
import { LoaderOverlay } from "../src/common/components/scaffold"
import { I18nextProvider } from "react-i18next"
import { initialize, mswLoader } from "msw-storybook-addon"
import { withRouter } from "storybook-addon-remix-react-router"
import mswHandlers from "./mocks"
import useUserManager, { UserContext } from "../src/carbure/hooks/user"
import { EntityContext, useEntityManager } from "../src/carbure/hooks/entity"
import { PortalProvider } from "../src/common/components/portal"
import { MatomoProvider } from "../src/matomo"

import "../src/setup-dsfr"
// import css from our app
import "../src/carbure/assets/css/index.css"

// Init MSW
initialize()

const withI18next = (Story, context) => {
  const { locale } = context.globals

  useEffect(() => {
    i18n.changeLanguage(locale)
  }, [locale])

  return (
    <I18nextProvider i18n={i18n}>
      <Story />
    </I18nextProvider>
  )
}

const withData = (Story) => {
  const user = useUserManager()
  const entityId = user?.user?.rights[0]?.entity.id
  const entity = useEntityManager(user, entityId)

  if (user.loading) {
    return <LoaderOverlay />
  }
  return (
    <Suspense fallback={<LoaderOverlay />}>
      <MatomoProvider>
        <UserContext.Provider value={user}>
          <EntityContext.Provider value={entity}>
            <PortalProvider>
              <div className="new-dsfr">
                <Story />
              </div>
            </PortalProvider>
          </EntityContext.Provider>
        </UserContext.Provider>
      </MatomoProvider>
    </Suspense>
  )
}

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    msw: {
      handlers: mswHandlers,
    },
  },
  loaders: [mswLoader],
}

export const globalTypes = {
  locale: {
    name: "Locale",
    description: "Internationalization locale",
    toolbar: {
      icon: "globe",
      items: [
        { value: "fr", title: "French" },
        { value: "en", title: "English" },
      ],
      showName: true,
    },
  },
}

export const decorators = [withData, withI18next, withRouter]

export default preview
