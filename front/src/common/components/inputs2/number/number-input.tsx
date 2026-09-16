import { formatNumber } from "common/utils/formatters"
import { Input, InputProps } from "../input"

export type NumberInputProps = InputProps & {
  min?: number
  max?: number
  step?: number
  unit?: string
  fractionDigits?: number
  value?: number | null
  onChange?: (value: number | undefined) => void
}

export const NumberInput = ({
  value,
  onChange,
  min,
  max,
  step,
  readOnly,
  readOnlyValue,
  ...props
}: NumberInputProps) => {
  const formattedValue =
    readOnly && value !== undefined && value !== null
      ? formatNumber(value)
      : undefined
  return (
    <Input
      {...props}
      readOnly={readOnly}
      readOnlyValue={readOnlyValue ?? formattedValue}
      type="number"
      nativeInputProps={{
        min,
        max,
        step,
        value: value ?? "",
        onChange: !onChange
          ? undefined
          : (e) => {
              const value = parseFloat(e.target.value)
              const change = isNaN(value) ? undefined : value
              onChange(change)
            },
      }}
    />
  )
}
