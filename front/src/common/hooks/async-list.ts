import { compact, matches } from "common/utils/collection"
import { useAsync, useAsyncCallback, UseAsyncReturn } from "react-async-hook"
import {
  Normalizer,
  Filter,
  normalizeItems,
  denormalizeItems,
  labelize,
} from "../utils/normalize"
import { staleWhileLoading } from "./async"

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

      // nothing to do if there's no selection
      if (values.length === 0) return EMPTY

      const cachedItems = [
        ...(asyncSelectedItems.result ?? []),
        ...(asyncItems.result ?? []),
        ...(defaultItems ?? []),
        ...(items ?? []),
      ]

      function findCachedItem(value: V) {
        return cachedItems.find((item) => matches(value, normalize(item).value))
      }

      // look for cached versions of the current values
      const valuesCachedItems = compact(values.map(findCachedItem))

      // nothing to do if we already have items for each value
      if (valuesCachedItems.length === values.length) {
        return valuesCachedItems
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
          const foundItems = await findItems("")
          return foundItems.find((item) => matches(value, normalize(item).value)); // prettier-ignore
        })

        const results = await Promise.all(promises)
        availableItems = results.filter((r) => r !== undefined) as T[]
      }

      // filter items matching the selection
      const keys = values.map(sortedStringify)
      const isSelected: Filter<T, V> = (item) => keys.includes(sortedStringify(item.value)) // prettier-ignore
      const normItems = normalizeItems(availableItems, normalize, isSelected)
      return denormalizeItems(normItems)
    },
    [selectedValue, selectedValues, items, defaultItems],
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

// make sure that when an object is stringified, its keys are always sorted in alphabetical order
// this allows easy deep comparison between two objects, even with nested data
function sortedStringify(jsonLike: any) {
  return JSON.stringify(jsonLike, (_, value) => {
    if (value instanceof Array || !(value instanceof Object)) return value

    return Object.keys(value)
      .sort()
      .reduce((sorted, key) => {
        sorted[key] = value[key]
        return sorted
      }, {} as Record<string, any>)
  })
}
