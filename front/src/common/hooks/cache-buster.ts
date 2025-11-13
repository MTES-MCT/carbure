import i18next from "i18next"
import { useEffect, useRef } from "react"
import { useLocation } from "react-router"

const ETAG_CACHE_KEY = "carbure:cache:etag"

export function useCacheBuster() {
  useRouteChange()
  useVisibilityChange()
}

// Watch for change in routes to trigger a cache bust
function useRouteChange() {
  const lastPath = useRef<string>()
  const location = useLocation()

  useEffect(() => {
    if (!lastPath.current || location.pathname != lastPath.current) {
      lastPath.current = location.pathname
      cacheBuster()
    }
  }, [location.pathname])
}

// Watch for when the user leaves the tab/window and gets back to it later
function useVisibilityChange() {
  useEffect(() => {
    function handler() {
      if (document.visibilityState === "visible") {
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
async function cacheBuster() {
  const cachedEtag = getCachedEtag()
  const remoteEtag = await fetchRemoteEtag()

  if (remoteEtag && cachedEtag != remoteEtag) {
    if (promptReload()) {
      cacheEtag(remoteEtag)
      window.location.reload()
    }
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
