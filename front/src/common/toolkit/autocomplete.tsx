import React, { useEffect, useRef, useState } from "react"
import cl from "clsx"
import { DOMProps } from "./types"
import { RelativeOverlay } from "./overlay"
import { Registry, useRegistry } from "./registry"
import { SingleChoice } from "./single-choice"

export const stringify = (value: any) => `${value ?? ""}`

export type AutocompleteProps<T> = DOMProps<
  HTMLInputElement,
  {
    value?: T
    onChange?: (value: T | undefined) => void
    onQuery?: (query: string) => void
    serialize?: (value: T | undefined) => string
    children?: React.ReactNode
  }
>

export function Autocomplete<T>({
  domRef,
  value,
  className,
  children,
  onQuery,
  onChange: setValue,
  serialize = stringify,
  ...props
}: AutocompleteProps<T>) {
  const options = useRegistry<T>()

  const localRef = useRef<HTMLInputElement>(null)
  const ref = domRef ?? localRef

  const [open, showOptions] = useState(false)
  const [query, setQuery] = useState("")

  // effect to update the query when the value is changed from above
  useEffect(() => {
    const label = serialize(value)
    if (label !== query) {
      setQuery(label)
    }
  }, [value, query, serialize])

  // effect to update the value when the query directly matches one of the options
  useEffect(() => {
    const option = options.entries.find((o) => serialize(o.value) === query)
    if (option && option.value !== value) {
      setValue?.(option.value)
    }
  }, [value, query, options.entries, serialize, setValue])

  // change the value and update the query
  function onValueChange(value: T | undefined) {
    setValue?.(value)
    setQuery(serialize(value))
  }

  // change the query and trigger callback
  async function onQueryChange(query: string) {
    setQuery(query)
    onQuery?.(query)

    if (query === "" && value !== undefined) {
      setValue?.(undefined)
    }
  }

  return (
    <>
      <input
        {...props}
        ref={ref}
        value={query}
        autoComplete="off"
        className={cl("autocomplete", { open }, className)}
        onChange={(e) => onQueryChange(e.target.value)}
        onFocus={(e) => {
          onQuery?.(query)
          showOptions(true)
          props.onFocus?.(e)
        }}
        onBlur={(e) => {
          showOptions(false)
          props.onBlur?.(e)
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !open) e.preventDefault()
          if (e.key === "Enter") showOptions(!open)
          if (e.key === "Escape") showOptions(false)
          if (e.key === "ArrowUp") onValueChange(options.before(value))
          if (e.key === "ArrowDown") onValueChange(options.after(value))
          props.onKeyDown?.(e)
        }}
      />

      <RelativeOverlay hidden={!open} at={ref} className="autocomplete-options">
        <Registry value={options}>
          <SingleChoice value={value} onChange={onValueChange}>
            {children}
          </SingleChoice>
        </Registry>
      </RelativeOverlay>
    </>
  )
}

export default Autocomplete
