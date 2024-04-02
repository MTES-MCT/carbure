import { useRef, useState } from "react"
import { useAsyncList } from "../hooks/async-list"
import { defaultNormalizer, Normalizer, Sorter } from "../utils/normalize"
import Dropdown, { Trigger } from "./dropdown"
import { ChevronDown } from "./icons"
import { Control, Input } from "./input"
import List from "./list"
import cl from "clsx"
import css from "./select.module.css"

export interface SelectProps<T, V = T> extends Control, Trigger {
  clear?: boolean
  search?: boolean
  value?: V | undefined
  options?: T[]
  defaultOptions?: T[]
  placeholder?: string
  getOptions?: () => Promise<T[]>
  onChange?: (value: V | undefined) => void
  normalize?: Normalizer<T, V>
  sort?: Sorter<T, V>
}

export function Select<T, V>({
  clear,
  search,
  value,
  placeholder = "Select an option",
  options,
  defaultOptions,
  loading,
  getOptions,
  onChange,
  onOpen,
  onClose,
  anchor,
  normalize = defaultNormalizer,
  sort,
  ...props
}: SelectProps<T, V>) {
  const triggerRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)

  const asyncOptions = useAsyncList({
    selectedValue: value,
    items: options,
    defaultItems: defaultOptions,
    getItems: getOptions,
    normalize,
  })

  const onClear =
    clear && value !== undefined && onChange
      ? () => onChange(undefined) // prettier-ignore
      : undefined

  return (
    <div className={cl(css.select)}>

      <Input
        {...props}
        domRef={triggerRef}
        type="text"
        placeholder={placeholder}
        onChange={(e) => e}
        value={asyncOptions.label}
        icon={<ChevronDown passthrough />}
        onClear={onClear}
        loading={loading || asyncOptions.loading}
      />

      {!props.disabled && !props.readOnly && (
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
            sort={sort}
            normalize={normalize}
            onFocus={onChange}
            onSelectValue={(value) => {
              onChange?.(value)
              setOpen(false)
            }}
          />
        </Dropdown>
      )}
    </div>
  )
}

export default Select
