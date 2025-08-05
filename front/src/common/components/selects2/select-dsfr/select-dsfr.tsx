import { Select, SelectProps } from "@codegouvfr/react-dsfr/SelectNext"
import { defaultNormalizer, Normalizer } from "common/utils/normalize"

const defaultGetValue = <T, V = T>(value: V) => {
  if (typeof value === "string") return value
  if (typeof value === "number") return value.toString()
  if (typeof value === "boolean") return value.toString()

  console.error(
    "The value used inside the select is a complex data, define a getValue function to handle it (base html select only support string values)"
  )
  return ""
}

export type SelectDsfrProps<T, V = T> = Omit<
  SelectProps<SelectProps.Option[]>,
  "options"
> & {
  value?: V | undefined
  getValue?: (value: V) => string
  options: T[]
  onChange?: (value: V | undefined) => void
  normalize?: Normalizer<T, V>
}

export const SelectDsfr = <T, V = T>({
  value,
  getValue = defaultGetValue,
  options,
  onChange,
  normalize = defaultNormalizer,
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

  return (
    <Select
      {...props}
      nativeSelectProps={{
        value: selectedOption?.value,
        onChange: onChange ? (e) => onChange(e.target.value as V) : undefined,
      }}
      options={normalizedOptions}
    />
  )
}
