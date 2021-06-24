import React from "react"
import cl from "clsx"
import { DOMProps, Merge } from "./types"
import { useEntry } from "./registry"
import { useMultipleChoice } from "./multiple-choice"

export type CheckboxProps = DOMProps<
  HTMLInputElement,
  {
    children?: React.ReactNode
    onChange?: (value: boolean) => void
  }
>

export const Checkbox = ({
  domRef,
  className,
  style,
  children,
  onChange,
  ...props
}: CheckboxProps) => (
  <label className={cl("checkbox", className)}>
    <input
      {...props}
      ref={domRef}
      type="checkbox"
      onChange={onChange ? (e) => onChange(e.target.checked) : undefined}
    />
    {children}
  </label>
)

export function CheckboxOption<T>({
  domRef,
  value,
  ...props
}: Merge<CheckboxProps, { value: T }>) {
  const entry = useEntry(value, props.children, domRef)
  const choice = useMultipleChoice()

  return (
    <Checkbox
      domRef={entry.ref}
      name={choice.name}
      checked={choice.value.includes(value)}
      onChange={() => choice.onChange(value)}
      {...props}
    />
  )
}

export default Checkbox
