import React, { useContext, useLayoutEffect } from "react"
import { useLocation } from "react-router-dom"

type PushArgs = [string, ...any[]][]

declare global {
  interface Window {
    _paq?: Pick<PushArgs, "push">
  }
}

export const TrackerContext = React.createContext(() => [])
export const useTracker = () => useContext(TrackerContext)()

export const TrackerProvider = (props: any) => {
  const location = useLocation()

  const value = () => window._paq ?? []

  useLayoutEffect(() => {
    const tracker = value()
    tracker.push(["setCustomUrl", window.location.href])
    tracker.push(["trackPageView"])
  }, [location.pathname])

  return React.createElement(TrackerContext.Provider, { ...props, value })
}
