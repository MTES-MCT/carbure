import {
  useAsync,
  useAsyncCallback,
  UseAsyncCallbackOptions,
  UseAsyncOptions,
} from "react-async-hook"
import { invalidate, useInvalidate } from "./invalidate"

export type QueryOptions<R, A extends any[]> = UseAsyncOptions<R> & {
  key: string
  params: A
}

export function useQuery<R, A extends any[]>(
  asyncFunction: (...args: A) => Promise<R>,
  { key, params, ...options }: QueryOptions<R, A>
) {
  const query = useAsync(asyncFunction, params, {
    ...options,
    ...staleWhileLoading,
  })

  useInvalidate(key, () => query.execute(...params))

  return query
}

export type MutationOptions<R> = UseAsyncCallbackOptions<R> & {
  invalidates?: string[]
}

export function useMutation<R, A extends any[]>(
  asyncFunction: (...args: A) => Promise<R>,
  { invalidates, ...options }: MutationOptions<R> = {}
) {
  return useAsyncCallback(asyncFunction, {
    ...options,
    ...staleWhileLoading,
    onSuccess: (res, opts) => {
      // invalidate linked queries if mutation is successful
      if (invalidates) invalidate?.(...invalidates)
      options.onSuccess?.(res, opts)
    },
  })
}

export const staleWhileLoading = {
  setLoading: (state: any) => ({ ...state, loading: true }),
}
