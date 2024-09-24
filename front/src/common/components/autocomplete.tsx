import { useAsyncList } from "common/hooks/async-list"
import { matches } from "common/utils/collection"
import { useEffect, useRef, useState } from "react"
import {
  defaultNormalizer,
  Normalizer,
  normalizeItems,
  denormalizeItems,
  Sorter,
} from "../utils/normalize"
import Dropdown, { Trigger } from "./dropdown"
import { Control, TextInput } from "./input"
import List, { createQueryFilter, defaultRenderer, Renderer } from "./list"

export interface AutocompleteProps<T, V = T> extends Control, Trigger {
  value?: V | undefined
  options?: T[]
  defaultOptions?: T[]
  inputRef?: React.RefObject<HTMLInputElement>
  getOptions?: (query: string) => Promise<T[]>
  onChange?: (value: V | undefined) => void
  onQuery?: (query: string) => void
  onSelect?: (value: V | undefined) => void
  create?: (value: string) => V
  normalize?: Normalizer<T, V>
  children?: Renderer<T, V>
  sort?: Sorter<T, V>
}

function Autocomplete<T, V>({
  loading,
  value,
  options,
  defaultOptions,
  inputRef,
  getOptions,
  onChange,
  onQuery,
  onSelect,
  create,
  anchor,
  normalize = defaultNormalizer,
  children = defaultRenderer,
  sort,
  ...props
}: AutocompleteProps<T, V>) {
  const triggerRef = useRef<HTMLInputElement>(null)

  const autocomplete = useAutocomplete({
    value,
    options,
    defaultOptions,
    getOptions,
    onChange,
    onQuery,
    create,
    normalize,
  })

  return (
    <>
      <TextInput
        {...props}
        placeholder={props.readOnly ? undefined : props.placeholder}
        autoComplete={false}
        loading={loading || autocomplete.loading}
        inputRef={inputRef}
        domRef={triggerRef}
        value={autocomplete.query}
        onChange={autocomplete.onQuery}
      />

      {!props.disabled && !props.readOnly && (
        <Dropdown
          open={autocomplete.open && autocomplete.suggestions.length > 0}
          triggerRef={triggerRef}
          onOpen={autocomplete.execute}
          onToggle={autocomplete.setOpen}
          anchor={anchor}
        >
          <List
            controlRef={triggerRef}
            items={autocomplete.suggestions}
            selectedValue={value}
            children={children}
            normalize={normalize}
            onFocus={onChange}
            onSelectValue={(key: V | undefined) => {
              autocomplete.onSelect(key)
              onSelect && onSelect(key)
            }}
            sort={sort}
          />
        </Dropdown>
      )}
    </>
  )
}

interface AutocompleteConfig<T, V> {
  value?: V | undefined
  options?: T[]
  defaultOptions?: T[]
  getOptions?: (query: string) => Promise<T[]>
  onChange?: (value: V | undefined) => void
  onQuery?: (query: string) => void
  create?: (value: string) => V
  normalize?: Normalizer<T, V>
}

export function useAutocomplete<T, V>({
  value,
  options,
  defaultOptions,
  getOptions,
  onChange,
  onQuery,
  create,
  normalize = defaultNormalizer,
}: AutocompleteConfig<T, V>) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")

  const asyncOptions = useAsyncList<T, V>({
    selectedValue: value,
    items: options,
    defaultItems: defaultOptions,
    findItems: getOptions,
    normalize,
  })

  // update query when selected values label change
  useEffect(() => {
    setQuery(asyncOptions.label)
  }, [asyncOptions.label])

  useEffect(() => {
    if (value === undefined) setQuery("")
  }, [value])

  const [suggestions, setSuggestions] = useState(options ?? [])
  useEffect(() => setSuggestions(asyncOptions.items), [asyncOptions.items])

  function filterOptions(query: string): T[] {
    const options = asyncOptions.items
    const includesQuery = createQueryFilter(query)
    return denormalizeItems(
      normalizeItems<T, V>(options, normalize, includesQuery)
    )
  }

  function matchQuery(
    query: string,
    options: T[],
    create?: (query: string) => V
  ) {
    const isQuery = createQueryFilter<T, V>(query, true)
    const itemMatches = normalizeItems(options, normalize, isQuery)
    const match = itemMatches.length > 0 ? itemMatches[0] : undefined

    if (match && !matches(match.value, value)) {
      onChange?.(match.value)
    } else if (create) {
      onChange?.(create(query))
    }
  }

  const defaultQuery = query
  async function onQueryChange(query: string = defaultQuery) {
    setQuery(query ?? "")
    onQuery?.(query ?? "")

    // reset autocomplete value if query is emptied
    if (query === undefined || query === "") onChange?.(undefined)
    // stop here if we emptied the input with the clear button
    if (query === undefined) return setOpen(false)

    // otherwise, the user is typing so show the dropdown
    setOpen(true)

    // find options that could match the current query
    const suggestions = filterOptions(query)

    // set them as suggestions and check if one of them matches the query exactly
    setSuggestions(suggestions)
    matchQuery(query, suggestions, create)

    // if we fetch the options asyncly, start it now
    if (getOptions) {
      const nextOptions = await asyncOptions.execute(query)
      if (nextOptions) matchQuery(query, nextOptions)
    }
  }

  function onSelect(value: V | undefined) {
    onChange?.(value)
    setOpen(false)

    const norm = asyncOptions.items
      ?.map(normalize)
      .find((item) => item.value === value)

    if (norm) {
      // reeset query and filter options based on the selected value label
      setQuery(norm.label ?? "")
      setSuggestions(filterOptions(norm.label))
    }
  }

  return {
    loading: asyncOptions.loading,
    query,
    suggestions,
    open,
    setOpen,
    execute: () => asyncOptions.execute(query),
    onQuery: onQueryChange,
    onSelect,
  }
}

export default Autocomplete
