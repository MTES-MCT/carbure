import React, { useEffect, useRef, useState } from "react"

import styles from "./dropdown.module.css"

import { LabelInput, LabelInputProps } from "."
import { DropdownItem, DropdownOptions, useDropdown } from "./dropdown"
import useAPI from "../../hooks/helpers/use-api"

function useAutoComplete<T>(
  value: T,
  name: string,
  queryArgs: any[],
  onChange: (e: any) => void,
  getLabel: (option: T) => string,
  getQuery: (q: string, ...a: any[]) => Promise<T[]>
) {
  const dd = useDropdown()

  const [query, setQuery] = useState(getLabel(value))
  const [suggestions, resolveQuery] = useAPI(getQuery)

  // on change, modify the query to match selection and send event to parent
  function change(value: T) {
    setQuery(getLabel(value))
    onChange({ target: { name, value } })
    dd.toggle(false)
  }

  function onQuery(e: React.ChangeEvent<HTMLInputElement>) {
    const query = e.target.value
    setQuery(query)

    if (query.length === 0) {
      dd.toggle(false)
    } else {
      dd.toggle(true)
      resolveQuery(query, ...queryArgs)
    }
  }

  // modify input content when passed value is changed
  useEffect(() => {
    setQuery(getLabel(value))
  }, [value, getLabel])

  return { dd, query, suggestions, onQuery, change }
}

type AutoCompleteProps<T> = Omit<LabelInputProps, "value"> & {
  value: T
  options?: T[]
  queryArgs?: any[]
  getValue: (option: T) => string
  getLabel: (option: T) => string
  onChange: (e: any) => void
  getQuery: (q: string, ...a: any[]) => Promise<T[]>
}

function AutoComplete<T>({
  value,
  name,
  queryArgs = [],
  readOnly,
  onChange,
  getValue,
  getLabel,
  getQuery,
  ...props
}: AutoCompleteProps<T>) {
  const container = useRef<HTMLDivElement>(null)

  const { dd, query, suggestions, onQuery, change } = useAutoComplete(
    value,
    name!,
    queryArgs,
    onChange,
    getLabel,
    getQuery
  )

  const isEmpty = !suggestions.data || suggestions.data.length === 0

  return (
    <div ref={container}>
      <LabelInput
        {...props}
        value={query}
        readOnly={readOnly}
        onChange={onQuery}
        onBlur={() => dd.toggle(false)}
      />

      {!readOnly && !isEmpty && dd.isOpen && container.current && (
        <DropdownOptions
          parent={container.current}
          options={suggestions.data!}
          className={styles.suggestions}
          onChange={change}
        >
          {(options, focused) =>
            options.map((o, i) => (
              <DropdownItem
                key={getValue(o)}
                focused={focused === i}
                onClick={() => change(o)}
              >
                {getLabel(o)}
              </DropdownItem>
            ))
          }
        </DropdownOptions>
      )}
    </div>
  )
}

export default AutoComplete
