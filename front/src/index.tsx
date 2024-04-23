import React, { Suspense } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"

import "./i18n"
import "./carbure/assets/css/index.css"

import Carbure from "./carbure"
import { MatomoProvider } from "./matomo"
import { LoaderOverlay } from "common/components/scaffold"
import { setupWorker } from "msw"
import * as elecAdminAuditMocks from "elec-audit-admin/__test__/api"
import * as elecMocks from "elec/__test__/api"


if (process.env.NODE_ENV === "development") {
  console.log("DEV MODE")
  const worker = setupWorker(
    ...Object.values(elecAdminAuditMocks),
    ...Object.values(elecMocks)
  )
  worker.start()
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
