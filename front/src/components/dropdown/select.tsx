import React, { useState } from "react"
import cl from "clsx"

import styles from "./select.module.css"

import { SystemProps } from "../system"
import { Cross } from "../icons"
import { Dropdown, useDropdown } from "./dropdown"

export type Option = {
  key: string | number
  label: string
}

type SelectLabelProps = SystemProps & {
  value: Option["key"] | Option["key"][] | null
  placeholder?: string
  onChange: (value: SelectLabelProps["value"]) => void
}

type SelectProps = SelectLabelProps & {
  options: Option[]
  search?: boolean
  multiple?: boolean
}

// check if the value is empty
function isEmpty(value: SelectProps["value"]) {
  if (Array.isArray(value)) {
    return value.length === 0
  } else {
    return value ?? true
  }
}

// check if the given opton is selected
function isSelected(value: SelectProps["value"], option: Option) {
  if (Array.isArray(value)) {
    return value.includes(option.key)
  } else {
    return value === option.key
  }
}

// combine selected values in one element with their label
function renderSelected(value: SelectProps["value"], options: Option[]) {
  if (Array.isArray(value)) {
    return options
      .filter((o) => value.includes(o.key))
      .map((v) => v.label)
      .join(", ")
  } else {
    return options.find((o) => o.key === value)?.label
  }
}

function useSelect(
  value: SelectProps["value"],
  placeholder: string | undefined,
  options: Option[],
  onChange: SelectProps["onChange"],
  multiple: boolean
) {
  const dd = useDropdown()
  const [query, setQuery] = useState("")

  // reset the value
  function clear(e: React.MouseEvent) {
    onChange(null)
    setQuery("")
  }

  // select an option
  function select(e: React.MouseEvent, option: Option) {
    if (multiple && Array.isArray(value)) {
      // prevent closing of option list
      e.stopPropagation()

      if (value.includes(option.key)) {
        onChange(value.filter((key) => key !== option.key))
      } else {
        onChange([...value, option.key])
      }
    } else {
      onChange(option.key)
    }
  }

  // what to display in the dropdown label
  const selected =
    renderSelected(value, options) || placeholder || "Choisir une valeur"

  // filter options according to search query
  const queryOptions =
    query.length > 0
      ? options.filter((option) => option.label.toLowerCase().includes(query))
      : options

  return { dd, selected, queryOptions, query, select, clear, setQuery }
}

export const Select = ({
  value,
  placeholder,
  options,
  onChange,
  children,
  search = false,
  multiple = false,
  ...props
}: SelectProps) => {
  const {
    dd,
    query,
    selected,
    queryOptions,
    clear,
    select,
    setQuery,
  } = useSelect(value, placeholder, options, onChange, multiple)

  return (
    <Dropdown {...props} onClick={dd.toggle}>
      <Dropdown.Label className={styles.selectLabel}>
        <span title={selected} className={styles.selectValue}>
          {selected}
        </span>

        {!isEmpty(value) && (
          <Cross className={styles.selectCross} onClick={clear} />
        )}
      </Dropdown.Label>

      <Dropdown.Items open={dd.isOpen}>
        {search && (
          <li>
            <input
              type="text"
              value={query}
              placeholder="Rechercher..."
              className={styles.selectSearch}
              onChange={(e) => setQuery(e.target.value.toLowerCase())}
              onClick={(e) => e.stopPropagation()}
            />
          </li>
        )}

        {queryOptions.map((option) => (
          <li
            key={option.key}
            title={option.label}
            onClick={(e) => select(e, option)}
            className={cl(isSelected(value, option) && styles.selectSelected)}
          >
            {multiple && (
              <input
                readOnly
                type="checkbox"
                checked={isSelected(value, option)}
                className={styles.selectMultiple}
              />
            )}

            {option.label}
          </li>
        ))}
      </Dropdown.Items>
    </Dropdown>
  )
}

export default Select
