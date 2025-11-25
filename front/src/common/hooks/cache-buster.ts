import i18next from "i18next"
import { useEffect, useRef } from "react"
import { useLocation } from "react-router"

const ETAG_CACHE_KEY = "carbure:cache:etag"

const logger = (...args: any[]) => {
  if (isDevMode) {
    console.log(...args)
  }
}

const isCacheBusterRunning: { current: boolean } = { current: false }

const isDevMode = import.meta.env.DEV

export function useCacheBuster() {
  useFirstLoad()
  useRouteChange()
  useVisibilityChange()
}

function useFirstLoad() {
  useEffect(() => {
    logger("----- FIRST LOAD -----")

    cacheBuster(true)
  }, [])
}

function useRouteChange() {
  const lastPath = useRef<string>()
  const location = useLocation()

  useEffect(() => {
    logger("----- ROUTE CHANGE -----")
    if (!lastPath.current || location.pathname != lastPath.current) {
      lastPath.current = location.pathname

      if (!isCacheBusterRunning) {
        logger("----- CACHE BUSTER RUN FOR ROUTE CHANGE -----")
        cacheBuster()
      }
    }
  }, [location.pathname])
}

// Watch for when the user leaves the tab/window and gets back to it later
function useVisibilityChange() {
  useEffect(() => {
    function handler() {
      if (document.visibilityState === "visible") {
        logger("----- CACHE BUSTER RUN FOR VISIBILITY CHANGE -----")
        cacheBuster()
      }
    }

    document.addEventListener("visibilitychange", handler)
    return () => {
      document.removeEventListener("visibilitychange", handler)
    }
  }, [])
}

// compare the currently cached etag with the one fetched from the server
// and prompt the user for a full reload if a change was detected
async function cacheBuster(silentReload = false) {
  if (isDevMode) return

  // Éviter les exécutions multiples simultanées
  if (isCacheBusterRunning.current) {
    logger("----- CACHE BUSTER ALREADY RUNNING -----")
    return
  }

  isCacheBusterRunning.current = true

  try {
    const cachedEtag = getCachedEtag()
    const remoteEtag = await fetchRemoteEtag()
    logger("----- CACHE BUSTER EXECUTED -----", cachedEtag, remoteEtag)
    if (!cachedEtag && remoteEtag) {
      cacheEtag(remoteEtag)
    } else if (remoteEtag && cachedEtag != remoteEtag) {
      if (silentReload || promptReload()) {
        cacheEtag(remoteEtag)
        window.location.reload()
      }
    }
  } finally {
    isCacheBusterRunning.current = false
  }
}

function promptReload() {
  return confirm(
    i18next.t(
      "Une mise à jour est disponible. Souhaitez-vous recharger l'application ?"
    )
  )
}

async function fetchRemoteEtag() {
  try {
    const response = await fetch("/index.html", {
      method: "HEAD",
      cache: "no-store",
    })

    return response.headers.get("etag")
  } catch {
    return null
  }
}

function getCachedEtag() {
  return localStorage.getItem(ETAG_CACHE_KEY)
}

function cacheEtag(etag: string) {
  localStorage.setItem(ETAG_CACHE_KEY, etag)
}
