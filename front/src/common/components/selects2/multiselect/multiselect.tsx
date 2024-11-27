import { Button, ButtonProps } from "common/components/button2"
import { Trigger } from "common/components/dropdown2"
import { Control } from "common/components/input"
import { useAsyncList } from "common/hooks/async-list"
import { defaultNormalizer, Normalizer, Sorter } from "common/utils/normalize"
import { useRef } from "react"
import cl from "clsx"
import styles from "./multiselect.module.css"

export interface MultiSelectProps<T, V = T> extends Control, Trigger {
  clear?: boolean
  search?: boolean
  value?: V[] | undefined
  placeholder?: string
  options?: T[]
  getOptions?: () => Promise<T[]>
  onChange?: (value: V[] | undefined) => void
  normalize?: Normalizer<T, V>
  sort?: Sorter<T, V>

  size?: ButtonProps["size"]

  // If true, the select will take the full width of its container
  full?: boolean
  className?: string
}

export const MultiSelect = <T, V>({
  loading,
  value,
  placeholder = "Select options",
  options,
  getOptions,
  // onChange,
  normalize = defaultNormalizer,
  full,
  size,
  className,
}: MultiSelectProps<T, V>) => {
  const triggerRef = useRef<HTMLButtonElement>(null)
  // const [open, setOpen] = useState(false)

  const asyncOptions = useAsyncList({
    selectedValues: value,
    items: options,
    getItems: getOptions,
    normalize,
  })

  // function onClear() {
  //   onChange?.(undefined)
  //   setOpen(false)
  // }

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
        {asyncOptions.label || placeholder}
      </Button>
    </>
  )
}
