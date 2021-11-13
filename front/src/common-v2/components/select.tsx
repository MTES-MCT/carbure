import { useRef, useState } from "react"
import { useAsyncList } from "../hooks/async"
import { defaultNormalizer, Normalizer } from "../utils/normalize"
import Dropdown, { Trigger } from "./dropdown"
import { ChevronDown } from "./icons"
import { Control, Input } from "./input"
import List from "./list"

export interface SelectProps<T, V> extends Control, Trigger {
  clear?: boolean
  search?: boolean
  value?: V | undefined
  options?: T[]
  placeholder?: string
  getOptions?: () => Promise<T[]>
  onChange?: (value: V | undefined) => void
  normalize?: Normalizer<T, V>
}

export function Select<T, V>({
  clear,
  search,
  value,
  placeholder = "Select an option",
  options,
  getOptions,
  onChange,
  onOpen,
  onClose,
  anchor,
  normalize = defaultNormalizer,
  ...props
}: SelectProps<T, V>) {
  const triggerRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)

  const asyncOptions = useAsyncList({
    selectedValue: value,
    items: options,
    getItems: getOptions,
    normalize,
  })

  const onClear =
    clear && value !== undefined && onChange
      ? () => onChange(undefined) // prettier-ignore
      : undefined

  return (
    <>
      <Input
        {...props}
        domRef={triggerRef}
        type="button"
        value={asyncOptions.label || placeholder}
        icon={ChevronDown}
        onClear={onClear}
        loading={asyncOptions.loading}
      />

      <Dropdown
        open={open && asyncOptions.items.length > 0}
        triggerRef={triggerRef}
        anchor={anchor}
        onClose={onClose}
        onToggle={setOpen}
        onOpen={() => {
          onOpen?.()
          asyncOptions.execute()
        }}
      >
        <List
          controlRef={triggerRef}
          search={search}
          items={asyncOptions.items}
          selectedValue={value}
          normalize={normalize}
          onFocus={onChange}
          onSelectValue={(value) => {
            onChange?.(value)
            setOpen(false)
          }}
        />
      </Dropdown>
    </>
  )
}

export default Select
