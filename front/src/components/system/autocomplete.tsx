import React, { useEffect, useState } from "react"

import { LabelInput, LabelInputProps } from "."

import styles from "./autocomplete.module.css"

import Dropdown, { useDropdown } from "./dropdown"
import useAPI from "../../hooks/helpers/use-api"

function useAutoComplete<T>(
  value: T,
  name: string,
  onChange: (e: any) => void,
  getLabel: (option: T) => string,
  getQuery: (query: string) => Promise<T[]>
) {
  const dd = useDropdown()

  const [query, setQuery] = useState("")
  const [suggestions, resolve] = useAPI<[string], T[]>(getQuery)

  // modify input content when passed value is changed
  useEffect(() => {
    setQuery(getLabel(value))
  }, [value, getLabel])

  // refetch the list of suggestions when query changes
  useEffect(() => {
    return resolve(query).cancel
  }, [query, getQuery, resolve])

  // on change, modify the query to match selection and send event to parent
  function change(value: T) {
    setQuery(getLabel(value))
    onChange({ target: { name, value } })
  }

  // open the suggestions box according to current state
  function openSuggestions() {
    if (query.length > 0 && suggestions.data && suggestions.data.length > 0) {
      dd.toggle(true)
    } else {
      dd.toggle(false)
    }
  }

  return { dd, query, suggestions, setQuery, change, openSuggestions }
}

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
  onChange,
  getValue,
  getLabel,
  getQuery,
  ...props
}: AutoCompleteProps<T>) {
  const {
    query,
    dd,
    suggestions,
    setQuery,
    change,
    openSuggestions,
  } = useAutoComplete(value, name!, onChange, getLabel, getQuery)

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
