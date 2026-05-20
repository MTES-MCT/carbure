import {
  useMutation as useReactQueryMutation,
  useQueryClient,
  type QueryKey,
  type UseMutationOptions as ReactQueryUseMutationOptions,
  type UseMutationResult,
} from "@tanstack/react-query"

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

export function useMutation<
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

export {
  useQuery,
  useQueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
export type { QueryKey, UseQueryOptions } from "@tanstack/react-query"
