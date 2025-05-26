import React from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter } from "react-router-dom"

import "./i18n"
import "./common/assets/css/index.css"

import Carbure from "./common"
import { MatomoProvider } from "./matomo"
import { SentryProvider, initSentry } from "./sentry"
import "./setup-dsfr"

initSentry()

async function enableMocking() {
  if (import.meta.env.MODE !== "development") return

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { worker } = await import("./mocks")
  console.info(
    "MOCKING ENABLED: to enable/disable the mocked api, comment/uncomment the line below in the file 'index.tsx'"
  )
  // return worker.start()
}

// After adding lazy loading inside routes, we need to reload the page when a preload error occurs (files saved in the cache are outdated and need to be reloaded)
window.addEventListener("vite:preloadError", (e) => {
  e.preventDefault()
  window.location.reload()
})

enableMocking().then(() =>
  createRoot(document.getElementById("root")!).render(
    <SentryProvider>
      <React.StrictMode>
        <BrowserRouter>
          <MatomoProvider>
            <Carbure />
          </MatomoProvider>
        </BrowserRouter>
      </React.StrictMode>
    </SentryProvider>
  )
)
