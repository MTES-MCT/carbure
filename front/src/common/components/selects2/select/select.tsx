import { useRef, useState } from "react"
import { useAsyncList } from "common/hooks/async-list"
import { defaultNormalizer, Normalizer, Sorter } from "common/utils/normalize"
import { Dropdown, Trigger } from "../../dropdown2"
import { List, ListProps } from "../../list2"
import { Button, ButtonProps } from "common/components/button2"
import styles from "./select.module.css"
import { Text } from "common/components/text"
import cl from "clsx"
export type SelectProps<T, V = T> = Trigger & {
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
  children?: ListProps<T, V>["children"]
  loading?: boolean
  style?: React.CSSProperties
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
  children,
  style,
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
        type="button"
        style={style}
      >
        <Text
          fontWeight="semibold"
          is="span"
          className={cl(!valueRenderer && styles.label)}
        >
          {currentItem && valueRenderer
            ? valueRenderer(currentItem)
            : asyncOptions.label || placeholder}
        </Text>
      </Button>

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
        className={cl(search && styles["select-dropdown"])}
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
        >
          {children}
        </List>
      </Dropdown>
    </>
  )
}
