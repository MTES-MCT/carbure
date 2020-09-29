import React, { useEffect, useState } from "react"

import { LabelInput, LabelInputProps } from "."
import { Option } from "./select"

import styles from "./autocomplete.module.css"

import Dropdown, { useDropdown } from "./dropdown"
import useAPI from "../../hooks/use-api"

// AUTOCOMPLETE COMPONENT

type AutoCompleteProps = LabelInputProps & {
  value: string
  options?: Option[]
  getOptions?: (query: string) => Promise<any>
  onChange?: (e: any) => void
}

const AutoComplete = ({
  value,
  name,
  options,
  getOptions,
  onChange,
  ...props
}: AutoCompleteProps) => {
  const dd = useDropdown()
  const [query, setQuery] = useState("")
  const [suggestions, resolve] = useAPI<Option[]>()

  useEffect(() => {
    const option = options?.find((o) => o.value.toString() === value)
    option && setQuery(option.label)
  }, [value, options])

  useEffect(() => {
    getOptions && resolve(getOptions(query))
  }, [query, getOptions, resolve])

  function change(option: Option) {
    setQuery(option.label)

    if (onChange) {
      onChange({ target: { name: name!, value: option.value.toString() } })
    }
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
        {suggestions.data?.map((o) => (
          <li key={o.value} onClick={() => change(o)}>
            {o.label}
          </li>
        ))}
      </Dropdown.Items>
    </Dropdown>
  )
}

export default AutoComplete
