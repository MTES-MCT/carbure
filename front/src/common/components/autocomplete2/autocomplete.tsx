import { useAsyncList } from "common/hooks/async-list"
import { matches } from "common/utils/collection"
import { useEffect, useRef, useState } from "react"

import { Dropdown, Trigger } from "../dropdown2"
import { TextInput } from "../inputs2/text"
import { List, createQueryFilter, defaultRenderer, Renderer } from "../list2"
import {
  defaultNormalizer,
  denormalizeItems,
  Filter,
  normalizeItems,
  Normalizer,
  Sorter,
} from "common/utils/normalize"
import { Text } from "../text"
import { Trans } from "react-i18next"
import { InputProps } from "../inputs2/input"
import { LoaderLine } from "../icon"

export type AutocompleteProps<T, V = T> = Trigger &
  InputProps & {
    value?: V
    options?: T[]
    defaultOptions?: T[]
    getOptions?: (query: string) => Promise<T[]>
    onChange?: (value: V | undefined) => void
    onQuery?: (query: string) => void
    onSelect?: (value: V | undefined) => void
    create?: (value: string) => V
    normalize?: Normalizer<T, V>
    children?: Renderer<T, V>
    sort?: Sorter<T, V>
    filter?: Filter<T, V>
    debounce?: number
  }

export function Autocomplete<T, V>({
  loading,
  value,
  options,
  defaultOptions,
  getOptions,
  onChange,
  onQuery,
  onSelect,
  create,
  anchor,
  normalize = defaultNormalizer,
  children = defaultRenderer,
  sort,
  filter,
  debounce = 300,
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
    filter,
    debounce,
  })

  return (
    <>
      <TextInput
        {...props}
        placeholder={props.readOnly ? undefined : props.placeholder}
        autoComplete={false}
        loading={false}
        inputRef={triggerRef}
        value={autocomplete.query}
        onChange={autocomplete.onQuery}
        iconId="ri-arrow-down-s-line"
      />

      {!props.disabled && !props.readOnly && (
        <Dropdown
          open={autocomplete.open && autocomplete.suggestions.length > 0}
          triggerRef={triggerRef}
          onOpen={autocomplete.execute}
          onToggle={autocomplete.setOpen}
          anchor={anchor}
        >
          {loading || autocomplete.loading ? (
            <Text style={{ padding: "10px", textAlign: "center" }}>
              <Trans>Chargement des résultats...</Trans>
              <LoaderLine size="sm" style={{ marginLeft: "4px" }} />
            </Text>
          ) : (
            <List
              controlRef={triggerRef}
              items={autocomplete.suggestions}
              selectedValue={value}
              normalize={normalize}
              onFocus={onChange}
              onSelectValue={(key: V | undefined) => {
                autocomplete.onSelect(key)
                onSelect?.(key)
              }}
              sort={sort}
            >
              {children}
            </List>
          )}
        </Dropdown>
      )}
    </>
  )
}

interface AutocompleteConfig<T, V> {
  value?: V
  options?: T[]
  defaultOptions?: T[]
  getOptions?: (query: string) => Promise<T[]>
  onChange?: (value: V | undefined) => void
  onQuery?: (query: string) => void
  create?: (value: string) => V
  normalize?: Normalizer<T, V>
  filter?: Filter<T, V>
  debounce?: number
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
  filter,
  debounce = 300,
}: AutocompleteConfig<T, V>) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const timeoutRef = useRef<number>()

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

  // Reset query to the previous value when dropdown is closed
  useEffect(() => {
    if (!open && asyncOptions.label !== query) {
      setQuery(asyncOptions.label)
    }
  }, [open])

  const [suggestions, setSuggestions] = useState(options ?? [])
  useEffect(() => setSuggestions(asyncOptions.items), [asyncOptions.items])

  function filterOptions(query: string): T[] {
    const options = asyncOptions.items
    const includesQuery = filter ?? createQueryFilter(query)
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
      const setOptions = async () => {
        const nextOptions = await asyncOptions.execute(query)
        if (nextOptions) matchQuery(query, nextOptions)
      }

      if (!debounce) setOptions()
      else {
        if (timeoutRef.current) window.clearTimeout(timeoutRef.current)
        timeoutRef.current = window.setTimeout(setOptions, debounce)
      }
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
