import React, { useEffect, useRef, useState } from "react"

import styles from "./autocomplete.module.css"

import useAPI from "../hooks/helpers/use-api"
import { Input, InputProps, Label, LabelProps } from "."
import { DropdownItem, DropdownOptions, useDropdown } from "./dropdown"
import { Cross } from "./icons"

function useAutoComplete<T>(
  value: T | null,
  name: string,
  queryArgs: any[],
  minLength: number,
  target: Element | null,
  onChange: (e: any) => void,
  getLabel: (option: T) => string,
  getQuery: (q: string, ...a: any[]) => Promise<T[]>
) {
  const dd = useDropdown(target)

  const [query, setQuery] = useState(value ? getLabel(value) : "")
  const [suggestions, resolveQuery] = useAPI(getQuery)

  // on change, modify the query to match selection and send event to parent
  function change(value: T) {
    setQuery(getLabel(value))
    onChange({ target: { name, value } })
    dd.toggle(false)
  }

  async function onQuery(
    e: React.ChangeEvent<HTMLInputElement> | React.MouseEvent<HTMLInputElement>
  ) {
    const query = "value" in e.target ? e.target.value : ""
    setQuery(query)

    if (query.length === 0) {
      onChange({ target: { name, value: null } })
    }

    if (query.length < minLength) {
      dd.toggle(false)
    } else {
      dd.toggle(true)

      const results = await resolveQuery(query, ...queryArgs)

      // check if the typed value matches a result from the api
      // if so, trigger the onChange callback
      if (results && results.length > 0 && query.length > 0) {
        const compare = query.toLowerCase()

        const suggestion = results.find((suggestion) => {
          return compare === getLabel(suggestion).toLowerCase()
        })

        if (suggestion) {
          onChange({ target: { name, value: suggestion } })
        }
      }
    }
  }

  // modify input content when passed value is changed
  useEffect(() => {
    setQuery(value ? getLabel(value) : "")
  }, [value, getLabel])

  return { dd, query, suggestions, onQuery, change }
}

type AutoCompleteProps<T> = Omit<InputProps, "value"> & {
  value: T | null
  options?: T[]
  queryArgs?: any[]
  minLength?: number
  getValue: (option: T) => string
  getLabel: (option: T) => string
  onChange: (e: any) => void
  getQuery: (q: string, ...a: any[]) => Promise<T[]>
}

export function AutoComplete<T>({
  value,
  name,
  queryArgs = [],
  readOnly,
  minLength = 1,
  onChange,
  getValue,
  getLabel,
  getQuery,
  ...props
}: AutoCompleteProps<T>) {
  const target = useRef<HTMLInputElement>(null)

  const { dd, query, suggestions, onQuery, change } = useAutoComplete(
    value,
    name!,
    queryArgs,
    minLength,
    target.current,
    onChange,
    getLabel,
    getQuery
  )

  const isEmpty = !suggestions.data || suggestions.data.length === 0

  return (
    <React.Fragment>
      <Input
        {...props}
        value={query}
        name={name}
        readOnly={readOnly}
        onChange={onQuery}
        innerRef={target}
        onClick={onQuery}
        onBlur={() => dd.toggle(false)}
      />

      {!readOnly && !isEmpty && dd.isOpen && target.current && (
        <DropdownOptions
          parent={target.current}
          options={suggestions.data!}
          onChange={change}
        >
          {(options, focused) =>
            options.map((o, i) => (
              <DropdownItem
                key={getValue(o)}
                focused={focused === i}
                title={getLabel(o)}
                onClick={() => change(o)}
              >
                <span>{getLabel(o)}</span>
              </DropdownItem>
            ))
          }
        </DropdownOptions>
      )}
    </React.Fragment>
  )
}

export function LabelAutoComplete<T>({
  label,
  error,
  tooltip,
  ...props
}: AutoCompleteProps<T> & LabelProps) {
  return (
    <Label label={label} error={error} tooltip={tooltip}>
      <AutoComplete {...props} />
    </Label>
  )
}

type MultiAutocompleteProps<T> = Omit<
  AutoCompleteProps<T>,
  "value" | "onChange"
> & {
  value: T[]
  onChange: (e: any) => void
}

export function MultiAutocomplete<T>({
  value,
  name,
  onChange,
  getLabel,
  getValue,
  ...props
}: MultiAutocompleteProps<T>) {
  function addValue(e: any) {
    // if the value is not already in the list, add it
    if (
      e.target.value !== null &&
      !value.some((v) => getValue(v) === getValue(e.target.value))
    ) {
      onChange({ target: { name, value: [...value, e.target.value] } })
    }
  }

  // remove the given value from the list
  function removeValue(option: T) {
    const next = value.filter((v) => getValue(v) !== getValue(option))
    onChange({ target: { name, value: next } })
  }

  return (
    <div className={styles.multiWrapper}>
      {value.map((v) => (
        <span key={getValue(v)} className={styles.multiValue}>
          {getLabel(v)}
          <Cross
            className={styles.multiValueDelete}
            onClick={(e) => {
              e.preventDefault()
              removeValue(v)
            }}
          />
        </span>
      ))}
      <AutoComplete<T>
        {...props}
        value={null}
        name={name}
        onChange={addValue}
        getValue={getValue}
        getLabel={getLabel}
        className={styles.multiInput}
      />
    </div>
  )
}
