import {
  useMutation as useReactQueryMutation,
  useQueryClient,
  type QueryKey,
  type UseMutationOptions as ReactQueryUseMutationOptions,
  type UseMutationResult,
} from "@tanstack/react-query"

/**
 * React Query wrappers for Carbure.
 * See front/docs/react-query.md for usage conventions and migration guide.
 */

type InvalidateKey = QueryKey | string

export type UseMutationOptions<
  TData = unknown,
  TError = Error,
  TVariables = void,
  TContext = unknown,
> = ReactQueryUseMutationOptions<TData, TError, TVariables, TContext> & {
  invalidates?: InvalidateKey[]
}

function normalizeQueryKey(key: InvalidateKey): QueryKey {
  return Array.isArray(key) ? key : [key]
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiFn = (...args: any[]) => any

type MutationVariables<TFn extends ApiFn> =
  Parameters<TFn> extends [] ? void : Parameters<TFn>

function useRunMutation<
  TData = unknown,
  TError = Error,
  TVariables = void,
  TContext = unknown,
>(
  options: UseMutationOptions<TData, TError, TVariables, TContext>
): UseMutationResult<TData, TError, TVariables, TContext> {
  const queryClient = useQueryClient()
  const { invalidates, onSuccess, ...mutationOptions } = options

  const wrappedOnSuccess: NonNullable<
    ReactQueryUseMutationOptions<
      TData,
      TError,
      TVariables,
      TContext
    >["onSuccess"]
  > = async (...args) => {
    if (invalidates?.length) {
      await Promise.all(
        invalidates.map((key) =>
          queryClient.invalidateQueries({ queryKey: normalizeQueryKey(key) })
        )
      )
    }

    return onSuccess?.(...args)
  }

  return useReactQueryMutation({
    ...mutationOptions,
    onSuccess: wrappedOnSuccess,
  })
}

/**
 * Same API as legacy `async`: `useMutation(apiFn, options)`.
 * `options` = React Query options + `invalidates`. No need to pass `mutationFn`.
 *
 * Variables for `mutate` / `mutateAsync`: `void` when the API has no args, otherwise
 * the tuple `Parameters<typeof apiFn>`.
 *
 * @example
 * import { COMMON_QUERY_KEYS, useMutation } from "common/hooks/async-rq"
 * import * as api from "../api"
 *
 * const requestAccess = useMutation(api.requestAccess, {
 *   invalidates: [COMMON_QUERY_KEYS.userSettings],
 *   onSuccess: () => notify(t("OK"), { variant: "success" }),
 * })
 *
 * // Multiple API args → tuple
 * await requestAccess.mutateAsync([entityId, role])
 *
 * // Single API arg → one-element tuple
 * await revokeMyself.mutateAsync([entityId])
 *
 * // No API args
 * logoutMutation.mutate()
 */
export function useMutation<TFn extends ApiFn>(
  fn: TFn,
  options?: Omit<
    UseMutationOptions<Awaited<ReturnType<TFn>>, Error, MutationVariables<TFn>>,
    "mutationFn"
  >
): UseMutationResult<Awaited<ReturnType<TFn>>, Error, MutationVariables<TFn>> {
  return useRunMutation({
    ...options,
    mutationFn: (variables) => {
      if (variables === undefined) {
        return (fn as () => ReturnType<TFn>)()
      }
      return fn(...(variables as Parameters<TFn>))
    },
  })
}

export {
  useQuery,
  useQueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
export type { QueryKey, UseQueryOptions } from "@tanstack/react-query"

export const COMMON_QUERY_KEYS = {
  userSettings: ["user-settings"] as const,
}
