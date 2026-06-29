import { Dropdown } from "common/components/dropdown2"
import { List } from "common/components/list2"
import { LabelProps, ReadOnlyValue } from "common/components/inputs2/base-input"
import { InputProps } from "common/components/inputs2/input"
import { matches } from "common/utils/collection"
import {
  defaultNormalizer,
  labelize,
  Normalizer,
  Sorter,
} from "common/utils/normalize"
import i18next from "i18next"
import { useRef, useState } from "react"
import { FormPickerTrigger } from "../combobox"
import Tag from "@codegouvfr/react-dsfr/Tag"

export type FormMultiSelectProps<T, V = T> = Omit<
  InputProps,
  "value" | "onChange" | "nativeInputProps" | "inputRef" | "iconId"
> & {
  value?: V[] | undefined
  options: T[]
  onChange?: (value: V[] | undefined) => void
  normalize?: Normalizer<T, V>
  search?: boolean
  sort?: Sorter<T, V>
  placeholder?: string
} & Pick<LabelProps, "hasTooltip" | "title">

/**
 * Form multiselect built on a read-only TextInput trigger + List multiple.
 * The dropdown stays open on each selection (unlike FormSelect).
 */
export const FormMultiSelect = <T, V = T>({
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
  placeholder = i18next.t("Sélectionner 1 ou plusieurs options"),
  ...props
}: FormMultiSelectProps<T, V>) => {
  const triggerRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)

  const selectedItems = options.filter((option) =>
    value?.some((selected) => matches(selected, normalize(option).value))
  )
  const displayLabel = labelize(selectedItems, normalize)

  if (props.readOnly) {
    return (
      <ReadOnlyValue
        label={label}
        hasTooltip={hasTooltip}
        title={title}
        readOnly={props.readOnly}
        value={displayLabel}
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
        displayValue={displayLabel}
        placeholder={placeholder}
      />

      {!props.disabled && (
        <Dropdown
          open={open && options.length > 0}
          triggerRef={triggerRef}
          onToggle={setOpen}
        >
          <List
            multiple
            search={search}
            controlRef={triggerRef}
            items={options}
            selectedValues={value}
            normalize={normalize}
            sort={sort}
            onSelectValues={onChange}
          />
        </Dropdown>
      )}
      {selectedItems.map((item) => (
        <Tag
          key={String(normalize(item).value)}
          dismissible
          small
          style={{ marginTop: "4px" }}
          nativeButtonProps={{
            onClick: () => {
              const removedItems = value?.filter(
                (_value) => _value !== normalize(item).value
              )
              onChange?.(removedItems)
            },
          }}
        >
          {normalize(item).label}
        </Tag>
      ))}
    </>
  )
}
