import React, { Suspense } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"

import "./i18n"
import "./carbure/assets/css/index.css"

import Carbure from "./carbure"
import { MatomoProvider } from "./matomo"
import { LoaderOverlay } from "common/components/scaffold"

async function enableMocking() {
  if (process.env.NODE_ENV === "development") {
    const { worker } = await import("./mocks")
    return worker.start()
  }
}

enableMocking().then(() =>
  createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <BrowserRouter>
        <MatomoProvider>
          <Suspense fallback={<LoaderOverlay />}>
            <Carbure />
          </Suspense>
        </MatomoProvider>
      </BrowserRouter>
    </React.StrictMode>
  )
)
