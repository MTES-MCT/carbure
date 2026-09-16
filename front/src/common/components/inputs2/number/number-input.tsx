import { formatNumber } from "common/utils/formatters"
import { ReadOnlyValue } from "../base-input"
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
  unit,
  fractionDigits,
  ...props
}: NumberInputProps) => {
  if (props.readOnly) {
    let formatted = ""
    if (value !== undefined && value !== null) {
      formatted = formatNumber(
        value,
        fractionDigits === undefined ? undefined : { fractionDigits }
      )
      if (unit) formatted = `${formatted} ${unit}`
    }

    return (
      <ReadOnlyValue
        label={props.label}
        hasTooltip={props.hasTooltip}
        title={props.title}
        readOnly={props.readOnly}
        value={formatted}
      />
    )
  }
  return (
    <Input
      {...props}
      type={props.readOnly ? "text" : "number"}
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
