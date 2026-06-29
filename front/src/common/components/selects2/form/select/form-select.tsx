import { Dropdown } from "common/components/dropdown2"
import { List } from "common/components/list2"
import { LabelProps, ReadOnlyValue } from "common/components/inputs2/base-input"
import { InputProps } from "common/components/inputs2/input"
import { matches } from "common/utils/collection"
import { defaultNormalizer, Normalizer, Sorter } from "common/utils/normalize"
import i18next from "i18next"
import { useRef, useState } from "react"
import { FormPickerTrigger } from "../combobox"

export type FormSelectProps<T, V = T> = Omit<
  InputProps,
  "value" | "onChange" | "nativeInputProps" | "inputRef" | "iconId"
> & {
  value?: V | undefined
  options: T[]
  onChange?: (value: V | undefined) => void
  normalize?: Normalizer<T, V>
  search?: boolean
  sort?: Sorter<T, V>
  placeholder?: string
} & Pick<LabelProps, "hasTooltip" | "title">

export const FormSelect = <T, V = T>({
  value,
  options,
  onChange,
  normalize = defaultNormalizer,
  label,
  hasTooltip,
  title,
  className,
  search,
  sort,
  placeholder = i18next.t("Sélectionner une option"),
  ...props
}: FormSelectProps<T, V>) => {
  const triggerRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)

  const selectedItem = options.find((option) =>
    value !== undefined ? matches(value, normalize(option).value) : false
  )
  const displayLabel = selectedItem ? normalize(selectedItem).label : undefined

  if (props.readOnly) {
    return (
      <ReadOnlyValue
        label={label}
        hasTooltip={hasTooltip}
        title={title}
        readOnly={props.readOnly}
        value={displayLabel ?? ""}
      />
    )
  }

  return (
    <>
      <FormPickerTrigger
        {...props}
        label={label}
        hasTooltip={hasTooltip}
        title={title}
        className={className}
        triggerRef={triggerRef}
        displayValue={displayLabel ?? ""}
        placeholder={placeholder}
      />

      {!props.disabled && (
        <Dropdown
          open={open && options.length > 0}
          triggerRef={triggerRef}
          onToggle={setOpen}
        >
          <List
            controlRef={triggerRef}
            search={search}
            items={options}
            selectedValue={value}
            normalize={normalize}
            sort={sort}
            onFocus={onChange}
            onSelectValue={(selected) => {
              onChange?.(selected)
              setOpen(false)
            }}
          />
        </Dropdown>
      )}
    </>
  )
}
