import React, { useRef, useState } from "react"
import cl from "clsx"
import { DOMProps } from "./types"
import { RelativeOverlay } from "./overlay"
import Registry, { useRegistry } from "./registry"
import MultipleChoice from "./multiple-choice"

export type MultipleSelectProps<T> = DOMProps<
  HTMLDivElement,
  {
    value?: T[] | undefined
    options?: T[]
    placeholder?: string
    onChange?: (value: T[] | undefined) => void
    children?: React.ReactNode
  }
>

export function MultipleSelect<T>({
  domRef,
  value = [],
  placeholder = "Select a value",
  children,
  onChange,
  ...props
}: MultipleSelectProps<T>) {
  const options = useRegistry<T>()

  const localRef = useRef<HTMLDivElement>(null)
  const ref = domRef ?? localRef

  const [open, showOptions] = useState(false)
  const [focus, setFocus] = useState<T | undefined>()

  function toggleValue(focus: T) {
    if (value?.includes(focus)) {
      onChange?.(value.filter((v) => v !== focus))
    } else {
      onChange?.([...value, focus])
    }
  }

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
          if (e.key === "Enter" && focus) toggleValue(focus)
          if (e.key === "ArrowUp") setFocus(options.before(focus))
          if (e.key === "ArrowDown") setFocus(options.after(focus))
          props.onKeyDown?.(e)
        }}
      >
        {value?.length} {placeholder}
      </div>

      <RelativeOverlay hidden={!open} at={ref} className="select-options">
        <Registry value={options}>
          <MultipleChoice value={value} onChange={onChange}>
            {children}
          </MultipleChoice>
        </Registry>
      </RelativeOverlay>
    </>
  )
}

export default MultipleSelect
