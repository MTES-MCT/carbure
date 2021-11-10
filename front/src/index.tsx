import React, { Suspense } from "react"
import ReactDOM from "react-dom"
import { BrowserRouter } from "react-router-dom"

import "./i18n"
import "./carbure/assets/css/index.css"
import "common-v2/reset.css"
import "common-v2/theme.css"
import * as serviceWorker from "./serviceWorker"

import Carbure from "./carbure"
import NotificationsProvider from "common/components/notifications"
import { MatomoProvider } from "./matomo"
import { LoaderOverlay } from "common/components"
import { PortalProvider } from "common-v2/components/portal"

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter basename="/v2">
      <MatomoProvider>
        <Suspense fallback={<LoaderOverlay />}>
          <NotificationsProvider>
            <PortalProvider>
              <Carbure />
            </PortalProvider>
          </NotificationsProvider>
        </Suspense>
      </MatomoProvider>
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById("root")
)

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.register()
