import { staleWhileLoading } from "common-v2/hooks/async"
import { useEffect, useRef, useState } from "react"
import { useAsyncCallback } from "react-async-hook"
import {
  defaultNormalizer,
  Filter,
  Normalizer,
  normalizeTree,
} from "../utils/normalize"
import { standardize as std } from "common-v2/formatters"
import Dropdown, { Trigger } from "./dropdown"
import { Control, TextInput } from "./input"
import List, { defaultRenderer, Renderer } from "./list"

export interface AutocompleteProps<T> extends Control, Trigger {
  value: T | undefined
  options?: T[]
  getOptions?: (query: string) => Promise<T[]>
  onChange: (value: T | undefined) => void
  onQuery?: (query: string) => void
  normalize?: Normalizer<T>
  children?: Renderer<T>
}

function Autocomplete<T>({
  loading,
  value,
  options,
  getOptions,
  onChange,
  onQuery,
  anchor,
  normalize = defaultNormalizer,
  children = defaultRenderer,
  ...props
}: AutocompleteProps<T>) {
  const triggerRef = useRef<HTMLInputElement>(null)

  const autocomplete = useAutocomplete({
    value,
    options,
    getOptions,
    onChange,
    onQuery,
    normalize,
  })

  return (
    <>
      <TextInput
        {...props}
        loading={loading || autocomplete.loading}
        domRef={triggerRef}
        value={autocomplete.query}
        onChange={autocomplete.onQuery}
      />

      <Dropdown
        open={autocomplete.open && autocomplete.options.length > 0}
        triggerRef={triggerRef}
        onOpen={() => autocomplete.onQuery(autocomplete.query)}
        onToggle={autocomplete.setOpen}
        anchor={anchor}
      >
        <List
          controlRef={triggerRef}
          items={autocomplete.options}
          selectedItem={value}
          children={children}
          normalize={normalize}
          onFocus={onChange}
          onSelectItem={autocomplete.onSelect}
        />
      </Dropdown>
    </>
  )
}

interface AutocompleteConfig<T> {
  value: T | undefined
  options?: T[]
  getOptions?: (query: string) => Promise<T[]>
  onChange: (value: T | undefined) => void
  onQuery?: (query: string) => void
  normalize?: Normalizer<T>
}

export function useAutocomplete<T>({
  value,
  options: controlledOptions,
  getOptions,
  onChange,
  onQuery: controlledOnQuery,
  normalize = defaultNormalizer,
}: AutocompleteConfig<T>) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")

  const label = value ? normalize(value).label : ""
  useEffect(() => setQuery(label), [label])

  const [options, setOptions] = useState(controlledOptions ?? [])
  useEffect(() => setOptions(controlledOptions ?? []), [controlledOptions])

  const asyncOptions = useAsyncCallback(
    (query: string) => getOptions?.(query),
    {
      ...staleWhileLoading,
      onSuccess: (res) => res && setOptions(res),
    }
  )

  const baseOptions = asyncOptions.result ?? controlledOptions ?? []

  function matchQuery(query: string, options: T[]) {
    const key = value ? normalize(value).key : ""
    const stdQuery = std(query)
    const match = options.find((item) => std(normalize(item).label) === stdQuery) // prettier-ignore
    if (match && normalize(match).key !== key) onChange(match)
  }

  async function onQuery(query: string | undefined) {
    setQuery(query ?? "")

    // reset autocomplete value if query is emptied
    if (!query) onChange(undefined)

    // stop here if we just cleared the input
    if (query === undefined) return
    // and open the dropdown otherwise
    else setOpen(true)

    const matches = filterOptions(query, baseOptions, normalize)

    setOptions(matches)
    matchQuery(query, matches)
    controlledOnQuery?.(query)

    if (getOptions) {
      const nextOptions = await asyncOptions.execute(query)
      if (nextOptions) matchQuery(query, nextOptions)
    }
  }

  function onSelect(value: T | undefined) {
    onChange(value)
    setOpen(false)

    // filter options based on the selected value label
    const query = value ? normalize(value).label : ""
    const matches = filterOptions(query, baseOptions, normalize)
    setOptions(matches)
  }

  return {
    loading: asyncOptions.loading,
    query,
    options,
    open,
    setOpen,
    onQuery,
    onSelect,
  }
}

export function filterOptions<T>(
  query: string,
  options: T[],
  normalize: Normalizer<T>
) {
  const stdQuery = std(query)
  const filter: Filter<T> = (item) => std(item.label).includes(stdQuery)
  return normalizeTree(options, normalize, filter).map((o) => o.value)
}

export default Autocomplete
