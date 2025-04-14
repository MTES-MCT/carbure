import { useAsyncList } from "common/hooks/async-list"
import {
  defaultNormalizer,
  denormalizeItems,
  normalizeItems,
  Normalizer,
} from "common/utils/normalize"
import { useEffect, useState } from "react"
import { createQueryFilter } from "../list2"
import { matches } from "common/utils/collection"

interface AutocompleteConfig<T, V> {
  value: V[] | undefined
  options?: T[]
  defaultOptions?: T[]
  getOptions?: (query: string) => Promise<T[]>
  onChange?: (value: V[] | undefined) => void
  onQuery?: (query: string) => Promise<T[] | void> | T[] | void
  normalize?: Normalizer<T, V>
}

export function useTagAutocomplete<T, V>({
  value = [],
  options,
  defaultOptions,
  getOptions,
  onChange,
  onQuery,
  normalize = defaultNormalizer,
}: AutocompleteConfig<T, V>) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")

  const asyncOptions = useAsyncList({
    selectedValues: value,
    items: options,
    defaultItems: defaultOptions,
    findItems: getOptions,
    normalize,
  })
  const [suggestions, setSuggestions] = useState(asyncOptions.items)
  useEffect(() => setSuggestions(asyncOptions.items), [asyncOptions.items])

  function filterOptions(query: string): T[] {
    const options = suggestions
    const includesQuery = createQueryFilter(query)
    return denormalizeItems(
      normalizeItems<T, V>(options, normalize, includesQuery)
    )
  }

  async function onQueryChange(query: string | undefined = "") {
    setQuery(query)
    setOpen(true)
    onQuery?.(query)

    const matches = filterOptions(query)
    setSuggestions(matches)

    // if we fetch the options asyncly, start it now
    if (getOptions) {
      await asyncOptions.execute(query)
    }
  }

  function onSelect(values: V[] | undefined) {
    onQueryChange("")
    onChange?.(values)
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Backspace" && query === "") {
      onChange?.(value.slice(0, -1))
    }
  }

  const allOptions = [...asyncOptions.items, ...(defaultOptions ?? [])]
  const tags = value
    .map((v) => allOptions.find((o) => matches(v, normalize(o).value)))
    .filter(Boolean) as T[]

  return {
    open,
    loading: asyncOptions.loading,
    query,
    tags,
    suggestions,
    setOpen,
    onSelect,
    onKeyDown,
    onQuery: onQueryChange,
  }
}
