import { isProduction } from "carbure/utils/production"
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

	const value = () => {
		const matomo = window._paq ?? []
		const push = (args: [string, ...any[]]) => {
			// only track production
			if (isProduction()) {
				matomo.push(args)
			}
		}
		return { push } as Matomo
	}

	useLayoutEffect(() => {
		const matomo = value()
		matomo.push(["disableCookies"])
		matomo.push(["setCustomUrl", window.location.href])
		matomo.push(["trackPageView"])
	}, [location.pathname])

	return React.createElement(MatomoContext.Provider, { ...props, value })
}
