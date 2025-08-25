import { Select, SelectProps } from "@codegouvfr/react-dsfr/SelectNext"
import { InputProps } from "@codegouvfr/react-dsfr/Input"
import {
  Label,
  LabelProps,
  ReadOnlyValue,
} from "common/components/inputs2/base-input"
import { defaultNormalizer, Normalizer } from "common/utils/normalize"
import cl from "clsx"
import styles from "./select-dsfr.module.css"

const defaultGetValue = <T, V = T>(value: V) => {
  if (typeof value === "string") return value
  if (typeof value === "number") return value.toString()
  if (typeof value === "boolean") return value.toString()

  console.error(
    "The value used inside the select is a complex data, define a getValue function to handle it (base html select only support string values)"
  )
  return ""
}

// The state prop has different values than the InputProps.state, so we need to pick it from the InputProps and map it to the SelectProps.state
export type SelectDsfrProps<T, V = T> = Omit<
  SelectProps<SelectProps.Option[]>,
  "options" | "state"
> &
  Omit<LabelProps, "label"> & {
    value?: V | undefined
    getValue?: (value: V) => string
    options: T[]
    onChange?: (value: V | undefined) => void
    normalize?: Normalizer<T, V>
    label?: LabelProps["label"]
  } & Pick<InputProps, "state">

export const SelectDsfr = <T, V = T>({
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
  ...props
}: SelectDsfrProps<T, V>) => {
  const normalizedOptions = options?.map((option) => {
    const normalized = normalize(option)
    return {
      label: normalized.label,
      value: getValue(normalized.value),
    }
  })

  const selectedOption = value
    ? normalizedOptions.find((option) => option.value === getValue?.(value))
    : undefined

  if (props.readOnly) {
    return (
      <ReadOnlyValue
        label={label}
        hasTooltip={hasTooltip}
        title={title}
        readOnly={props.readOnly}
        value={selectedOption?.label ?? ""}
      />
    )
  }

  return (
    <Select
      {...props}
      nativeSelectProps={{
        value: selectedOption?.value,
        onChange: onChange ? (e) => onChange(e.target.value as V) : undefined,
        required: props.required,
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
      className={cl(className, styles["select-dsfr"])}
    />
  )
}
