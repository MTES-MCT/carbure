import { uniqueBy } from "common-v2/utils/collection"
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
  defaultItems?: T[]
  getItems?: () => Promise<T[]>
  findItems?: (query: string) => Promise<T[]>
  normalize: Normalizer<T, V>
}

const EMPTY: any[] = []

export function useAsyncList<T, V>({
  selectedValue,
  selectedValues,
  items,
  defaultItems,
  getItems,
  findItems,
  normalize,
}: AsyncListOptions<T, V>) {
  // fetch the list of items when needed
  const asyncItems = useAsyncCallback<T[]>((query?: string) => {
    if (getItems) return getItems()
    else if (findItems) return findItems(query ?? "")
    else return items ?? defaultItems ?? EMPTY
  }, staleWhileLoading)

  // fetch items matching the currently selected values everytime they change
  const asyncSelectedItems: UseAsyncReturn<T[]> = useAsync(
    async () => {
      const dirtyValues: V[] =
        selectedValue !== undefined // prettier-ignore
          ? [selectedValue]
          : selectedValues ?? EMPTY

      const values = dirtyValues.filter((v: any) => v !== "" && v !== undefined)
      const keys = values.map((value) => JSON.stringify(value))

      // nothing to do if there's no selection
      if (values.length === 0) return EMPTY

      const cachedItems = uniqueBy(
        [
          ...(defaultItems ?? []),
          ...(asyncSelectedItems.result ?? []),
          ...(asyncItems.result ?? []),
        ],
        (item) => JSON.stringify(normalize(item).value)
      )

      function findCachedItem(value: V) {
        const key = JSON.stringify(value)
        return cachedItems.find(
          (item) => JSON.stringify(normalize(item).value) === key
        )
      }

      // nothing to do if we already have items for each value or we still loading them
      if (values.every(findCachedItem)) {
        return cachedItems.filter((item) =>
          keys.includes(JSON.stringify(normalize(item).value))
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
          const key = JSON.stringify(value)
          const foundItems = await findItems("")
          return foundItems.find((i) => JSON.stringify(normalize(i).value) === key) // prettier-ignore
        })

        const results = await Promise.all(promises)
        availableItems = results.filter((r) => r !== undefined) as T[]
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

export const staleWhileLoading = {
  setLoading: (state: any) => ({ ...state, loading: true }),
}
