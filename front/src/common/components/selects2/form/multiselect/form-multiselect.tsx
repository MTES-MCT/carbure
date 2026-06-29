import { Select, SelectProps } from "@codegouvfr/react-dsfr/SelectNext"
import { InputProps } from "@codegouvfr/react-dsfr/Input"
import { Dropdown } from "common/components/dropdown2"
import { List } from "common/components/list2"
import {
  Label,
  LabelProps,
  ReadOnlyValue,
} from "common/components/inputs2/base-input"
import { matches } from "common/utils/collection"
import {
  defaultNormalizer,
  labelize,
  Normalizer,
  Sorter,
} from "common/utils/normalize"
import cl from "clsx"
import { useRef, useState } from "react"
import styles from "../select/form-select.module.css"
import i18next from "i18next"

const DISPLAY_VALUE = "__form_multiselect_display__"

const defaultGetValue = <T, V = T>(value: V) => {
  if (typeof value === "string") return value
  if (typeof value === "number") return value.toString()
  if (typeof value === "boolean") return value.toString()

  console.error(
    "The value used inside the select is a complex data, define a getValue function to handle it (base html select only support string values)"
  )
  return ""
}

export type FormMultiSelectProps<T, V = T> = Omit<
  SelectProps<SelectProps.Option[]>,
  "options" | "state"
> &
  Omit<LabelProps, "label"> & {
    value?: V[] | undefined
    getValue?: (value: V) => string
    options: T[]
    onChange?: (value: V[] | undefined) => void
    normalize?: Normalizer<T, V>
    label?: LabelProps["label"]
    name?: string
    search?: boolean
    sort?: Sorter<T, V>
  } & Pick<InputProps, "state">

/**
 * Form multiselect visually aligned with FormSelect (DSFR SelectNext).
 *
 * Custom behaviour — the component is built on two layers:
 *
 * 1. DSFR shell (`<Select>`)
 *    - Renders as `fr-select` with label, states (error/success), and placeholder.
 *    - The native `<select>` is controlled but its native dropdown is disabled
 *      (`onMouseDown: preventDefault`): it is only used for display and as a
 *      trigger for the custom dropdown.
 *    - A native `<select>` can only display one value at a time. To summarise
 *      multiple selections in the closed field, we inject a synthetic option
 *      (`DISPLAY_VALUE`) whose label is the concatenation of selected options
 *      (`labelize`). The native select points to this fake option; the real
 *      options are only kept for HTML rendering/accessibility.
 *    - With no selection, `value` stays empty/undefined: DSFR shows the
 *      placeholder (`placeholder` prop, i18n default).
 *
 * 2. Actual selection (`<Dropdown>` + `<List multiple>`)
 *    - This is where the user selects/deselects values.
 *    - The dropdown stays open on each click (unlike FormSelect).
 *    - Supports `search` and `sort` on the options list.
 *
 * The `value` prop is an array (`V[]`). In read-only mode, concatenated labels
 * are displayed via `ReadOnlyValue`, without a dropdown.
 */
export const FormMultiSelect = <T, V = T>({
  value,
  getValue = defaultGetValue,
  options,
  onChange,
  normalize = defaultNormalizer,
  label,
  hasTooltip,
  title,
  state,
  className,
  name,
  search,
  sort,
  placeholder = i18next.t("Sélectionner 1 ou plusieurs options"),
  ...props
}: FormMultiSelectProps<T, V>) => {
  const selectedItems = options.filter((option) =>
    value?.some((selected) => matches(selected, normalize(option).value))
  )
  const displayLabel = labelize(selectedItems, normalize)

  const optionEntries = options.map((option) => {
    const normalized = normalize(option)
    return {
      label: normalized.label,
      value: getValue(normalized.value),
      name: getValue(normalized.value),
    }
  })

  const normalizedOptions = displayLabel
    ? [
        {
          label: displayLabel,
          value: DISPLAY_VALUE,
          name: DISPLAY_VALUE,
        },
        ...optionEntries,
      ]
    : optionEntries

  const selectRef = useRef<HTMLSelectElement>(null)
  const [open, setOpen] = useState(false)

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
      <Select
        {...props}
        nativeSelectProps={{
          ref: selectRef,
          value: displayLabel ? DISPLAY_VALUE : undefined,
          required: props.required,
          name,
          onMouseDown: (e) => e.preventDefault(),
        }}
        options={normalizedOptions}
        label={
          <Label
            hasTooltip={hasTooltip}
            required={props.required}
            title={title}
            label={label}
          />
        }
        state={state === "success" ? "valid" : state}
        className={cl(className, styles["form-select"])}
        placeholder={placeholder}
      />

      <Dropdown
        open={open && options.length > 0}
        triggerRef={selectRef}
        onToggle={setOpen}
      >
        <List
          multiple
          search={search}
          controlRef={selectRef}
          items={options}
          selectedValues={value}
          normalize={normalize}
          sort={sort}
          onSelectValues={onChange}
        />
      </Dropdown>
    </>
  )
}
