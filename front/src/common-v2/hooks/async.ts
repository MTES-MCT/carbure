import {
  useAsync,
  useAsyncCallback,
  UseAsyncCallbackOptions,
} from "react-async-hook"
import { staleWhileLoading } from "./async-list"
import { invalidate, useInvalidate } from "./invalidate"

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
      invalidates && invalidate(...invalidates)
      options.onSuccess?.(res, opts)
    },
  })
}
