import { useRef, useState } from "react"
import { useAsyncList } from "common/hooks/async-list"
import { defaultNormalizer, Normalizer, Sorter } from "common/utils/normalize"
import Dropdown, { Trigger } from "../../dropdown"

import { Control } from "../../input"
import List from "../../list"
import styles from "./select.module.css"
import { ArrowDownSLine } from "common/components/icon"
import { Button2 } from "common/components/button2"

export interface SelectProps<T, V = T> extends Control, Trigger {
  clear?: boolean // A garder ?
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
  const triggerRef = useRef<HTMLButtonElement>(null)
  const [open, setOpen] = useState(false)

  const asyncOptions = useAsyncList({
    selectedValue: value,
    items: options,
    defaultItems: defaultOptions,
    getItems: getOptions,
    normalize,
  })

  // const currentLabel =

  return (
    <>
      <Button2
        nativeButtonProps={{ ref: triggerRef }}
        className={styles["select-button"]}
      >
        <span>{asyncOptions.label || placeholder}</span>
        <ArrowDownSLine size="sm" />
      </Button2>
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
    </>
  )
}
