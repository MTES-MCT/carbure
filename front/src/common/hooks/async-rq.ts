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

type CarbureMutationResult<TFn extends ApiFn> = Omit<
  UseMutationResult<Awaited<ReturnType<TFn>>, Error, MutationVariables<TFn>>,
  "mutate" | "mutateAsync" | "isPending"
>

export type ApiMutationResult<TFn extends ApiFn> =
  CarbureMutationResult<TFn> & {
    execute: (...args: Parameters<TFn>) => Promise<Awaited<ReturnType<TFn>>>
    loading: boolean
  }

function argsToVariables<TFn extends ApiFn>(
  args: Parameters<TFn>
): MutationVariables<TFn> {
  return (args.length === 0 ? undefined : args) as MutationVariables<TFn>
}

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
 * `options` = React Query options + `invalidates`. Trigger via `execute(...args)`.
 *
 * @example
 * const requestAccess = useMutation(api.requestAccess, {
 *   invalidates: [COMMON_QUERY_KEYS.userSettings],
 * })
 * await requestAccess.execute(entityId, role)
 */
export function useMutation<TFn extends ApiFn>(
  fn: TFn,
  options?: Omit<
    UseMutationOptions<Awaited<ReturnType<TFn>>, Error, MutationVariables<TFn>>,
    "mutationFn"
  >
): ApiMutationResult<TFn> {
  const { mutateAsync, isPending, ...mutation } = useRunMutation({
    ...options,
    mutationFn: (variables) => {
      if (variables === undefined) {
        return (fn as () => ReturnType<TFn>)()
      }
      return fn(...(variables as Parameters<TFn>))
    },
  })

  return {
    ...mutation,
    loading: isPending,
    execute: (...args: Parameters<TFn>) => mutateAsync(argsToVariables(args)),
  }
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
