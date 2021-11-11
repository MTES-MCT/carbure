import { useRef, useState } from "react"
import Dropdown, { Trigger } from "./dropdown"
import { ChevronDown } from "./icons"
import { Control, Input } from "./input"
import List from "./list"
import { defaultNormalizer, Normalizer } from "../utils/normalize"

export interface SelectProps<T> extends Control, Trigger {
  clear?: boolean
  search?: boolean
  value: T | undefined
  options: T[]
  placeholder?: string
  onChange: (value: T | undefined) => void
  normalize?: Normalizer<T>
}

export function Select<T>({
  clear,
  search,
  value,
  options,
  placeholder = "Select an option",
  onChange,
  onOpen,
  onClose,
  anchor,
  normalize = defaultNormalizer,
  ...props
}: SelectProps<T>) {
  const triggerRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)
  const label = value ? normalize(value).label : placeholder

  return (
    <>
      <Input
        {...props}
        domRef={triggerRef}
        type="button"
        value={label}
        icon={ChevronDown}
        onClear={clear && value ? () => onChange(undefined) : undefined}
      />

      <Dropdown
        open={open && options.length > 0}
        triggerRef={triggerRef}
        anchor={anchor}
        onOpen={onOpen}
        onClose={onClose}
        onToggle={setOpen}
      >
        <List
          controlRef={triggerRef}
          search={search}
          items={options}
          selectedItem={value}
          onFocus={onChange}
          onSelectItem={(value) => {
            onChange(value)
            setOpen(false)
          }}
        />
      </Dropdown>
    </>
  )
}

export default Select
