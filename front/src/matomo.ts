import React, { useContext, useLayoutEffect } from "react"
import { useLocation } from "react-router-dom"

export type Matomo = Pick<[string, ...any[]][], "push">

declare global {
  interface Window {
    _paq?: Matomo
  }
}

export const MatomoContext = React.createContext<() => Matomo>(() => [])
export const useMatomo = () => useContext(MatomoContext)()

export const MatomoProvider = (props: any) => {
  const location = useLocation()

  const value = () => window._paq ?? []

  useLayoutEffect(() => {
    // only track production
    if (window.location.hostname !== "carbure.beta.gouv.fr") return

    const matomo = value()
    matomo.push(["setCustomUrl", window.location.href])
    matomo.push(["trackPageView"])
  }, [location.pathname])

  return React.createElement(MatomoContext.Provider, { ...props, value })
}
