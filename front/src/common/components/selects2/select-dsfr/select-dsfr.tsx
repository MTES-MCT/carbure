import { Select } from "@codegouvfr/react-dsfr/SelectNext"
import { defaultNormalizer, Normalizer } from "common/utils/normalize"

export type SelectDsfrProps<T, V = T> = {
  value?: V | undefined
  options: T[]
  onChange?: (value: V | undefined) => void
  normalize?: Normalizer<T, V>
}
export const SelectDsfr = <T, V = T>({
  value,
  options,
  onChange,
  normalize = defaultNormalizer,
}: SelectDsfrProps<T, V>) => {
  const normalizedOptions = options?.map(normalize)

  const selectedOption = normalizedOptions.find(
    (option) => option.value === value
  )
  console.log("la value", { value, options, normalizedOptions, selectedOption })
  return (
    <Select
      nativeSelectProps={{
        // @ts-ignore DSFR require string value for the value prop
        value: selectedOption?.value,
        onChange: onChange ? (e) => onChange(e.target.value as V) : undefined,
      }}
      // @ts-ignore DSFR require an array of string for options
      options={normalizedOptions}
    />
  )
}
