import { useEffect } from 'react'

export function invalidate(...keys: string[]) {
  keys.forEach(key => window.dispatchEvent(new Event(`invalidate:${key}`)))
}

export function useInvalidate(
  key: string,
  query: () => Promise<any>
) {
  useEffect(() => {
    const callback = () => query()
    window.addEventListener(`invalidate:${key}`, callback)
    return () => window.removeEventListener(`invalidate:${key}`, callback)
  }, [query])

  return () => invalidate(key)
}

export default useInvalidate