import React, { useEffect, useRef, useState } from "react"
import cl from "clsx"

import styles from "./autocomplete.module.css"

import useAPI from "../hooks/use-api"
import { Input, InputProps, Label, LabelProps } from "./input"
import { DropdownItem, DropdownOptions, useDropdown } from "./dropdown"
import { Cross } from "./icons"

const rawGetLabel = (v: any) => `${v}`
const rawGetValue = (v: any) => `${v}`

function useAutoComplete<T>(
  value: T | string | null,
  name: string,
  queryArgs: any[],
  minLength: number,
  target: Element | null,
  loose: boolean,
  search: boolean,
  onChange: (e: any) => void,
  getLabel: (option: T) => string,
  getQuery: (q: string, ...a: any[]) => Promise<T[]>
) {
  const dd = useDropdown(target)
  const [suggestions, resolveQuery] = useAPI(getQuery)

  const [query, setQuery] = useState(() =>
    value === null ? "" : typeof value === "string" ? value : getLabel(value)
  )

  // on change, modify the query to match selection and send event to parent
  function change(value: T, close?: boolean) {
    setQuery(getLabel(value))
    onChange({ target: { name, value } })
    close && dd.toggle(false)
  }

  async function onQuery(
    e: React.ChangeEvent<HTMLInputElement> | React.FocusEvent<HTMLInputElement>
  ) {
    const query = "value" in e.target ? e.target.value : ""
    setQuery(query)

    if (query.length === 0) {
      onChange({ target: { name, value: null } })
    }

    if (query.length < minLength) {
      dd.toggle(false)
    } else if (search) {
      dd.toggle(true)

      const results = (await resolveQuery(query, ...queryArgs)) ?? []

      // check if the typed value matches a result from the api
      // if so, trigger the onChange callback
      const compared = query.toLowerCase()
      const suggestion = results.find((suggestion) => {
        return compared === getLabel(suggestion).toLowerCase()
      })

      if (suggestion) {
        onChange({ target: { name, value: suggestion } })
      } else if (loose) {
        onChange({ target: { name, value: query } })
      }
    } else if (loose) {
      onChange({ target: { name, value: query } })
    }
  }

  // modify input content when passed value is changed
  useEffect(() => {
    if (typeof value !== "string") {
      setQuery(value ? getLabel(value) : "")
    }
  }, [value, getLabel])

  return { dd, query, suggestions, onQuery, change }
}

export type AutoCompleteProps<T> = Omit<InputProps, "value"> & {
  value?: T | string | null
  options?: T[]
  queryArgs?: any[]
  minLength?: number
  loose?: boolean
  search?: boolean
  getValue?: (option: T) => string
  getLabel?: (option: T) => string
  onChange?: (e: any) => void
  getQuery?: (q: string, ...a: any[]) => Promise<T[]>
}

export function AutoComplete<T>({
  value = null,
  name,
  queryArgs = [],
  readOnly,
  minLength = 1,
  loose = false,
  search = true,
  onChange = () => {},
  getValue = rawGetValue,
  getLabel = rawGetLabel,
  getQuery = async () => [],
  ...props
}: AutoCompleteProps<T>) {
  const target = useRef<HTMLInputElement>(null)

  const { dd, query, suggestions, onQuery, change } = useAutoComplete(
    value,
    name!,
    queryArgs,
    minLength,
    target.current,
    loose,
    search,
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
        onFocus={onQuery}
        autoComplete="off"
        onBlur={() => dd.toggle(false)}
      />

      {search && !readOnly && !isEmpty && dd.isOpen && target.current && (
        <DropdownOptions
          liveUpdate
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

export type LabelAutoCompleteProps<T> = AutoCompleteProps<T> & LabelProps

export function LabelAutoComplete<T>({
  label,
  error,
  tooltip,
  required,
  disabled,
  readOnly,
  icon,
  ...props
}: LabelAutoCompleteProps<T>) {
  return (
    <Label
      label={label}
      error={error}
      tooltip={tooltip}
      required={required}
      disabled={disabled}
      readOnly={readOnly}
      icon={icon}
    >
      <AutoComplete {...props} readOnly={readOnly} disabled={disabled} />
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
  getValue = rawGetValue,
  getLabel = rawGetLabel,
  readOnly,
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
    <div
      className={cl(
        styles.multiWrapper,
        readOnly && styles.multiWrapperReadOnly
      )}
    >
      {value.map((v) => (
        <span key={getValue(v)} className={styles.multiValue}>
          {getLabel(v)}
          {!readOnly && (
            <Cross
              className={styles.multiValueDelete}
              onClick={(e) => {
                e.preventDefault()
                removeValue(v)
              }}
            />
          )}
        </span>
      ))}
      {!readOnly && (
        <AutoComplete<T>
          {...props}
          value={null}
          name={name}
          readOnly={readOnly}
          onChange={addValue}
          getValue={getValue}
          getLabel={getLabel}
          className={styles.multiInput}
        />
      )}
    </div>
  )
}
