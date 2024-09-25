import { useAsyncList } from "common/hooks/async-list"
import { matches } from "common/utils/collection"
import React, { useEffect, useRef, useState } from "react"
import {
  defaultNormalizer,
  denormalizeItems,
  normalizeItems,
  Normalizer,
  Sorter,
} from "../utils/normalize"
import Checkbox from "./checkbox"
import Dropdown, { Trigger } from "./dropdown"
import { Control, Field } from "./input"
import List, { createQueryFilter, Renderer } from "./list"
import { TagGroup } from "./tag"

export interface TagAutocompleteProps<T, V = T> extends Control, Trigger {
  value: V[] | undefined
  options?: T[]
  defaultOptions?: T[]
  getOptions?: (search: string) => Promise<T[]>
  onChange: (value: V[] | undefined) => void
  onQuery?: (query: string) => Promise<T[] | void> | T[] | void
  normalize?: Normalizer<T, V>
  children?: Renderer<T, V>
  sort?: Sorter<T, V>
}

function TagAutocomplete<T, V = T>({
  placeholder,
  value,
  options,
  defaultOptions,
  getOptions,
  onChange,
  onQuery,
  anchor,
  normalize = defaultNormalizer,
  ...props
}: TagAutocompleteProps<T, V>) {
  const triggerRef = useRef<HTMLInputElement>(null)

  const autocomplete = useTagAutocomplete({
    value,
    options,
    defaultOptions,
    getOptions,
    onChange,
    onQuery,
    normalize,
  })

  return (
    <>
      <Field {...props} domRef={triggerRef}>
        <TagGroup
          variant="info"
          readOnly={props.disabled || props.readOnly}
          items={autocomplete.tags}
          onDismiss={onChange}
          normalize={normalize}
        >
          <input
            readOnly={props.readOnly}
            disabled={props.disabled}
            placeholder={props.readOnly ? undefined : placeholder}
            value={autocomplete.query}
            onChange={(e) => autocomplete.onQuery(e.target.value)}
            onKeyDown={autocomplete.onKeyDown}
            style={{ padding: 0 }}
          />
        </TagGroup>
      </Field>

      {!props.disabled && !props.readOnly && (
        <Dropdown
          open={autocomplete.open && autocomplete.suggestions.length > 0}
          triggerRef={triggerRef}
          onOpen={() => autocomplete.onQuery(autocomplete.query)}
          onToggle={autocomplete.setOpen}
          anchor={anchor}
        >
          <List
            multiple
            controlRef={triggerRef}
            items={autocomplete.suggestions}
            selectedValues={value}
            onSelectValues={autocomplete.onSelect}
            normalize={normalize}
          >
            {({ selected, label }) => (
              <Checkbox readOnly value={selected}>
                {label}
              </Checkbox>
            )}
          </List>
        </Dropdown>
      )}
    </>
  )
}

interface AutocompleteConfig<T, V> {
  value: V[] | undefined
  options?: T[]
  defaultOptions?: T[]
  getOptions?: (query: string) => Promise<T[]>
  onChange: (value: V[] | undefined) => void
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
    onChange(values)
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Backspace" && query === "") {
      onChange(value.slice(0, -1))
    }
  }

  const allOptions = [...asyncOptions.items, ...(defaultOptions ?? [])]
  const tags = value
    .map((v) => allOptions.find((o) => matches(v, normalize(o).value)))
    .filter(Boolean) as T[]

  return {
    open,
    query,
    tags,
    suggestions,
    setOpen,
    onSelect,
    onKeyDown,
    onQuery: onQueryChange,
  }
}

export default TagAutocomplete
