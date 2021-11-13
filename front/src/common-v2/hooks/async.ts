import { uniqueBy } from "common-v2/utils/collection"
import { useCallback, useEffect } from "react"
import {
  useAsync,
  useAsyncCallback,
  UseAsyncCallbackOptions,
  UseAsyncReturn,
} from "react-async-hook"
import {
  Normalizer,
  Filter,
  normalizeItems,
  denormalizeItems,
  labelize,
} from "../utils/normalize"

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
    ...staleWhileLoading,
    onSuccess: (res, opts) => {
      // invalidate linked queries if mutation is successful
      invalidate(...invalidates)
      options.onSuccess?.(res, opts)
    },
  })
}

export interface AsyncListOptions<T, V> {
  selectedValue?: V
  selectedValues?: V[]
  items?: T[]
  getItems?: () => Promise<T[]>
  findItems?: (query: string) => Promise<T[]>
  normalize: Normalizer<T, V>
}

const EMPTY: any[] = []

export function useAsyncList<T, V>({
  selectedValue,
  selectedValues,
  items,
  getItems,
  findItems,
  normalize,
}: AsyncListOptions<T, V>) {
  // fetch the list of items when needed
  const asyncItems = useAsyncCallback((query?: string) => {
    if (getItems) return getItems()
    else if (findItems) return findItems(query ?? "")
    else return items ?? (EMPTY as T[])
  }, staleWhileLoading)

  // fetch items matching the currently selected values everytime they change
  const asyncSelectedItems: UseAsyncReturn<T[]> = useAsync(
    async () => {
      const values =
        selectedValue !== undefined // prettier-ignore
          ? [selectedValue]
          : selectedValues ?? (EMPTY as V[])

      // nothing to do if there's no selection
      if (values.length === 0) return EMPTY as T[]

      const cachedItems = uniqueBy(
        [...(asyncSelectedItems.result ?? []), ...(asyncItems.result ?? [])],
        (item) => normalize(item).value
      )

      function findCachedItem(value: V) {
        return cachedItems.find((item) => normalize(item).value === value)
      }

      // nothing to do if we already have items for each value or we still loading them
      if (values.every(findCachedItem)) {
        return cachedItems.filter((item) =>
          values.includes(normalize(item).value)
        )
      }

      // prepare an array to store the items potentially matching the selection
      let availableItems: T[] = []

      // use the local value if defined
      if (items) {
        availableItems = items
      }
      // or fetch all values at once
      else if (getItems) {
        availableItems = await getItems()
      }
      // or fetch each value individually
      else if (findItems) {
        // only fetch values for which we don't have any item already cached
        const promises = values.map(async (value) => {
          const selectedValueItem = findCachedItem(value)
          if (selectedValueItem) return selectedValueItem
          const foundItems = await findItems(String(value))
          return foundItems.length > 0 ? foundItems[0] : null
        })

        const results = await Promise.all(promises)
        availableItems = results.filter((r) => r !== null) as T[]
      }

      // filter items matching the selection
      const isSelected: Filter<T, V> = (item) => values.includes(item.value)
      const normItems = normalizeItems(availableItems, normalize, isSelected)
      return denormalizeItems(normItems)
    },
    [selectedValue, selectedValues, items],
    staleWhileLoading
  )

  return {
    loading: items ? false : asyncItems.loading ?? asyncSelectedItems.error,
    error: asyncItems.error ?? asyncSelectedItems.error,
    items: items ?? asyncItems.result ?? EMPTY,
    selectedItems: asyncSelectedItems.result,
    label: labelize(asyncSelectedItems.result ?? [], normalize),
    execute: asyncItems.execute,
  }
}

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

export const staleWhileLoading = {
  setLoading: (state: any) => ({ ...state, loading: true }),
}
