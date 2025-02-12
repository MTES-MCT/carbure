import { Button, ButtonProps } from "common/components/button2"
import { Dropdown, Trigger } from "common/components/dropdown2"
import { useAsyncList } from "common/hooks/async-list"
import { defaultNormalizer, Normalizer, Sorter } from "common/utils/normalize"
import { useRef, useState } from "react"
import cl from "clsx"
import styles from "./multiselect.module.css"
import { List } from "common/components/list2"
import { Text } from "common/components/text"
export interface MultiSelectProps<T, V = T> extends Trigger {
  clear?: boolean
  search?: boolean
  value?: V[] | undefined
  placeholder?: string
  options?: T[]
  getOptions?: () => Promise<T[]>
  onChange?: (value: V[] | undefined) => void
  normalize?: Normalizer<T, V>
  sort?: Sorter<T, V>
  loading?: boolean
  size?: ButtonProps["size"]

  // If true, the select will take the full width of its container
  full?: boolean
  className?: string
  readOnly?: boolean
  disabled?: boolean
}

export const MultiSelect = <T, V>({
  loading,
  value,
  placeholder = "Select options",
  options,
  getOptions,
  onChange,
  normalize = defaultNormalizer,
  full,
  size,
  className,
  search,
  sort,
  anchor,
  onOpen,
  onClose,
  ...props
}: MultiSelectProps<T, V>) => {
  const triggerRef = useRef<HTMLButtonElement>(null)
  const [open, setOpen] = useState(false)

  const asyncOptions = useAsyncList({
    selectedValues: value,
    items: options,
    getItems: getOptions,
    normalize,
  })

  return (
    <>
      <Button
        ref={triggerRef}
        iconId={
          loading || asyncOptions.loading
            ? "ri-loader-line"
            : "fr-icon-arrow-down-s-line"
        }
        iconPosition="right"
        priority="tertiary"
        className={cl(
          styles["select-button"],
          full && styles["select-button-full"],
          className
        )}
        size={size}
      >
        {value && value.length > 0 && (
          <Text is="span" className={styles.count} size="xs">
            {value.length}
          </Text>
        )}
        <span className={styles.label}>
          {asyncOptions.label || placeholder}
        </span>
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
            multiple
            search={search}
            controlRef={triggerRef}
            items={asyncOptions.items}
            selectedValues={value}
            onSelectValues={onChange}
            normalize={normalize}
            sort={sort}
          />
        </Dropdown>
      )}
    </>
  )
}
