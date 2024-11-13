import { useRef, useState } from "react"
import { useAsyncList } from "common/hooks/async-list"
import { defaultNormalizer, Normalizer, Sorter } from "common/utils/normalize"
import { Dropdown, Trigger } from "../../dropdown2"

import { Control } from "../../input"
import { List } from "../../list2"
import { Button, ButtonProps } from "common/components/button2"
import styles from "./select.module.css"
import { Text } from "common/components/text"
import cl from "clsx"

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

  // Custom renderer for the displayed value
  valueRenderer?: (item: T) => React.ReactNode
  sort?: Sorter<T, V>
  size?: ButtonProps["size"]

  // If true, the select will take the full width of its container
  full?: boolean
  className?: string
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
  valueRenderer,
  size = "medium",
  full,
  className,
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

  const currentItem = asyncOptions.items.find(
    (item) => normalize(item).value === value
  )

  return (
    <>
      <Button
        ref={triggerRef}
        iconId={loading ? "ri-loader-line" : "fr-icon-arrow-down-s-line"}
        iconPosition="right"
        priority="tertiary"
        className={cl(
          styles["select-button"],
          full && styles["select-button-full"],
          className
        )}
        size={size}
      >
        <Text fontWeight="semibold" is="span">
          {currentItem && valueRenderer
            ? valueRenderer(currentItem)
            : asyncOptions.label || placeholder}
        </Text>
      </Button>
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
