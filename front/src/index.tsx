import React, { Suspense } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"

import "./i18n"
import "./carbure/assets/css/index.css"
import * as serviceWorker from "./serviceWorker"

import Carbure from "./carbure"
import { MatomoProvider } from "./matomo"
import { LoaderOverlay } from "common/components/scaffold"

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter basename="/app">
      <MatomoProvider>
        <Suspense fallback={<LoaderOverlay />}>
          <Carbure />
        </Suspense>
      </MatomoProvider>
    </BrowserRouter>
  </React.StrictMode>
)

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.register()
