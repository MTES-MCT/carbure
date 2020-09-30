import React, { useEffect, useState } from "react"

import { LabelInput, LabelInputProps } from "."

import styles from "./autocomplete.module.css"

import Dropdown, { useDropdown } from "./dropdown"
import useAPI from "../../hooks/helpers/use-api"

// AUTOCOMPLETE COMPONENT

type AutoCompleteProps<T> = Omit<LabelInputProps, "value"> & {
  value: T
  options?: T[]
  getValue: (option: T) => string
  getLabel: (option: T) => string
  onChange: (e: any) => void
  getQuery: (query: string) => Promise<T[]>
}

function AutoComplete<T>({
  value,
  name,
  options,
  getValue,
  getLabel,
  getQuery,
  onChange,
  ...props
}: AutoCompleteProps<T>) {
  const dd = useDropdown()
  const [query, setQuery] = useState("")
  const [suggestions, resolve] = useAPI<T[]>()

  useEffect(() => {
    setQuery(getLabel(value))
  }, [value])

  useEffect(() => {
    getQuery && resolve(getQuery(query))
  }, [query, getQuery, resolve])

  function change(option: T) {
    setQuery(getLabel(option))
    onChange({ target: { name: name!, value: option } })
  }

  function openSuggestions() {
    if (query.length > 0 && suggestions.data && suggestions.data.length > 0) {
      dd.toggle(true)
    } else {
      dd.toggle(false)
    }
  }

  return (
    <Dropdown>
      <LabelInput
        {...props}
        value={query}
        onKeyDown={openSuggestions}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          setQuery(e.target.value)
        }
      />

      <Dropdown.Items open={dd.isOpen} className={styles.suggestions}>
        {suggestions.data?.map((option) => (
          <li key={getValue(option)} onClick={() => change(option)}>
            {getLabel(option)}
          </li>
        ))}
      </Dropdown.Items>
    </Dropdown>
  )
}

export default AutoComplete
