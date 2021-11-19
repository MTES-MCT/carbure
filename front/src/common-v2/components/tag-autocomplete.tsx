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
import List, { createQueryFilter, defaultRenderer, Renderer } from "./list"
import { TagGroup } from "./tag"

export interface TagAutocompleteProps<T, V> extends Control, Trigger {
  value: V[] | undefined
  options: T[]
  onChange: (value: V[] | undefined) => void
  onQuery?: (query: string) => Promise<T[] | void> | T[] | void
  normalize?: Normalizer<T, V>
  children?: Renderer<T, V>
  sort?: Sorter<T, V>
}

function TagAutocomplete<T, V>({
  placeholder,
  value,
  options,
  onChange,
  onQuery,
  anchor,
  normalize = defaultNormalizer,
  children = defaultRenderer,
  ...props
}: TagAutocompleteProps<T, V>) {
  const triggerRef = useRef<HTMLInputElement>(null)

  const autocomplete = useTagAutocomplete({
    value,
    options,
    onChange,
    onQuery,
    normalize,
  })

  return (
    <>
      <Field {...props} domRef={triggerRef}>
        <TagGroup
          variant="info"
          items={autocomplete.tags}
          onDismiss={onChange}
          normalize={normalize}
        >
          <input
            readOnly={props.readOnly}
            disabled={props.disabled}
            placeholder={placeholder}
            value={autocomplete.query}
            onChange={(e) => autocomplete.onQuery(e.target.value)}
            onKeyDown={autocomplete.onKeyDown}
          />
        </TagGroup>
      </Field>

      <Dropdown
        open={autocomplete.open && options.length > 0}
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
    </>
  )
}

interface AutocompleteConfig<T, V> {
  value: V[] | undefined
  options: T[]
  onChange: (value: V[] | undefined) => void
  onQuery?: (query: string) => Promise<T[] | void> | T[] | void
  normalize?: Normalizer<T, V>
}

export function useTagAutocomplete<T, V>({
  value = [],
  options,
  onChange,
  onQuery,
  normalize = defaultNormalizer,
}: AutocompleteConfig<T, V>) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")

  const [suggestions, setSuggestions] = useState(options)
  useEffect(() => setSuggestions(options), [options])

  function filterOptions(query: string): T[] {
    const options = suggestions
    const includesQuery = createQueryFilter(query)
    return denormalizeItems(normalizeItems(options, normalize, includesQuery))
  }

  async function onQueryChange(query: string | undefined = "") {
    setQuery(query)
    setOpen(true)
    onQuery?.(query)

    const matches = filterOptions(query)
    setSuggestions(matches)
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

  const tags = value
    .map((v) => options.find((o) => normalize(o).value === v))
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
