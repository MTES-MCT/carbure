import React, { Suspense } from "react"
import ReactDOM from "react-dom"
import { BrowserRouter } from "react-router-dom"

import "./i18n"
import "./carbure/assets/css/index.css"
import * as serviceWorker from "./serviceWorker"

import Carbure from "./carbure"
import NotificationsProvider from "common/components/notifications"
import { LoaderOverlay } from "common/components"

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter basename="/v2">
      <Suspense fallback={<LoaderOverlay />}>
        <NotificationsProvider>
          <Carbure />
        </NotificationsProvider>
      </Suspense>
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById("root")
)

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.register()
