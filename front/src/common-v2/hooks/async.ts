import { useEffect } from "react"
import {
  useAsync,
  useAsyncCallback,
  UseAsyncCallbackOptions,
} from "react-async-hook"

export type QueryOptions<R, A extends any[]> = UseAsyncCallbackOptions<R> & {
  key: string
  params: A
}

export function useQuery<R, A extends any[]>(
  asyncFunction: (...args: A) => Promise<R>,
  { key, params, ...options }: QueryOptions<R, A>
) {
  const query = useAsync(asyncFunction, params, {
    ...options,
    setLoading: (state) => ({ ...state, loading: true }),
  })

  useEffect(() => {
    const callback = () => query.execute(...params)
    window.addEventListener(`invalidate:${key}`, callback)
    return () => window.removeEventListener(`invalidate:${key}`, callback)
  }, [key, query, params])

  return query
}

export type MutationOptions<R, A extends any[]> = UseAsyncCallbackOptions<R> & {
  invalidates: string[]
  params: A
}

export function useMutation<R, A extends any[]>(
  asyncFunction: (...args: A) => Promise<R>,
  { invalidates, params, ...options }: MutationOptions<R, A>
) {
  return useAsyncCallback(() => asyncFunction(...params), {
    ...options,
    setLoading: (state) => ({ ...state, loading: true }),
    onSuccess: (res, opts) => {
      // invalidate linked queries if mutation is successful
      invalidate(...invalidates)
      options.onSuccess?.(res, opts)
    },
  })
}

export function invalidate(...keys: string[]) {
  keys.forEach((key) => window.dispatchEvent(new Event(`invalidate:${key}`)))
}
