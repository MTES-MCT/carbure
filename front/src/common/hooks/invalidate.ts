import { useCallback, useEffect } from "react"

export function useInvalidate(key: string, action: () => void) {
	useEffect(() => {
		window.addEventListener(`invalidate:${key}`, action)
		return () => window.removeEventListener(`invalidate:${key}`, action)
	}, [key, action])

	return useCallback(() => invalidate(key), [key])
}

export function invalidate(...keys: string[]) {
	keys.forEach((key) => window.dispatchEvent(new Event(`invalidate:${key}`)))
}
