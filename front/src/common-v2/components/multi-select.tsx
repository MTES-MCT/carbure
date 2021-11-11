import { useRef, useState } from "react"
import Dropdown, { Trigger } from "./dropdown"
import { ChevronDown } from "./icons"
import { Control, Input } from "./input"
import List from "./list"
import {
  defaultNormalizer,
  Normalizer,
  normalizeTree,
} from "../utils/normalize"
import Checkbox from "./checkbox"

export interface MultiSelectProps<T> extends Control, Trigger {
  clear?: boolean
  search?: boolean
  value: T[] | undefined
  options: T[]
  placeholder?: string
  onChange: (value: T[] | undefined) => void
  normalize?: Normalizer<T>
}

export function MultiSelect<T>({
  clear,
  search,
  value,
  options,
  placeholder = "Select options",
  onChange,
  onOpen,
  onClose,
  anchor,
  normalize = defaultNormalizer,
  ...props
}: MultiSelectProps<T>) {
  const triggerRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)

  const hasValue = Boolean(value && value.length)
  const normValue = normalizeTree(value ?? [], normalize)
  const label = normValue.map((v) => v.label).join(", ")

  function onClear() {
    onChange(undefined)
    setOpen(false)
  }

  return (
    <>
      <Input
        {...props}
        domRef={triggerRef}
        type="button"
        value={label || placeholder}
        icon={ChevronDown}
        onClear={clear && hasValue ? onClear : undefined}
      />

      <Dropdown
        open={open && options.length > 0}
        triggerRef={triggerRef}
        onOpen={onOpen}
        onClose={onClose}
        onToggle={setOpen}
        anchor={anchor}
      >
        <List
          multiple
          search={search}
          controlRef={triggerRef}
          items={options}
          selectedItems={value}
          onSelectItems={onChange}
          normalize={normalize}
        >
          {({ selected, label }) => (
            <Checkbox readOnly value={selected}>
              {label}
            </Checkbox>
          )}
        </List>
      </Dropdown>
    </>
  )
}

export default MultiSelect
