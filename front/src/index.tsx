import React, { Suspense } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"

import "./i18n"
import "./carbure/assets/css/index.css"

import Carbure from "./carbure"
import { MatomoProvider } from "./matomo"
import { LoaderOverlay } from "common/components/scaffold"
import { setupWorker } from "msw"
import apiMocks from "__test__/api"

if (process.env.NODE_ENV === "development") {
  const worker = setupWorker(...apiMocks)
  console.log("DEV MODE : to enable/disable the mocked api, comment/uncomment the line below in the file 'index.tsx'")
  // worker.start()
}

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
