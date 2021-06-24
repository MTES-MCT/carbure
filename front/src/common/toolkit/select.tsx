import React, { useRef, useState } from "react"
import cl from "clsx"
import { DOMProps } from "./types"
import { RelativeOverlay } from "./overlay"
import { Registry, useRegistry } from "./registry"
import { SingleChoice } from "./single-choice"

export type SelectProps<T> = DOMProps<
  HTMLDivElement,
  {
    value?: T | undefined
    options?: T[]
    placeholder?: string
    onChange?: (value: T | undefined) => void
    children?: React.ReactNode
  }
>

export function Select<T>({
  domRef,
  value,
  placeholder = "Select a value",
  children,
  onChange,
  ...props
}: SelectProps<T>) {
  const options = useRegistry<T>()
  const option = options.entries.find((o) => o.value === value)

  const localRef = useRef<HTMLDivElement>(null)
  const ref = domRef ?? localRef

  const [open, showOptions] = useState(false)

  return (
    <>
      <div
        {...props}
        ref={ref}
        tabIndex={0}
        className={cl("select", { open }, props.className)}
        onClick={(e) => {
          showOptions(!open)
          props.onClick?.(e)
        }}
        onBlur={(e) => {
          showOptions(false)
          props.onBlur?.(e)
        }}
        onKeyDown={(e) => {
          if (e.key === " ") showOptions(!open)
          if (e.key === "Escape") showOptions(false)
          if (e.key === "ArrowUp") onChange?.(options.before(value))
          if (e.key === "ArrowDown") onChange?.(options.after(value))
          props.onKeyDown?.(e)
        }}
      >
        {option?.label ?? placeholder}
      </div>

      <RelativeOverlay hidden={!open} at={ref} className="select-options">
        <Registry value={options}>
          <SingleChoice value={value} onChange={onChange}>
            {children}
          </SingleChoice>
        </Registry>
      </RelativeOverlay>
    </>
  )
}

export default Select
