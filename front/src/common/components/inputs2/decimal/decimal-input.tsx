import { formatNumber } from "common/utils/formatters"
import { ReadOnlyValue } from "../base-input"
import { Input } from "../input"
import { NumberInputProps } from "../number/number-input"

export type DecimalInputProps = Omit<NumberInputProps, "value" | "onChange"> & {
  value?: string | null
  onChange?: (value: string | undefined) => void
}

function parseDecimal(value: string | null | undefined): number | null {
  if (value === null || value === undefined || value === "") return null
  const parsed = Number(value.replace(",", "."))
  return Number.isFinite(parsed) ? parsed : null
}

function fractionDigitsFromStep(step?: number): number {
  if (step === undefined || step <= 0 || step >= 1) return 2
  const digits = -Math.round(Math.log10(step))
  return digits >= 0 ? digits : 2
}

export const DecimalInput = ({
  value,
  onChange,
  step,
  ...props
}: DecimalInputProps) => {
  if (props.readOnly) {
    const parsed = parseDecimal(value)
    return (
      <ReadOnlyValue
        label={props.label}
        hasTooltip={props.hasTooltip}
        title={props.title}
        readOnly={props.readOnly}
        value={
          parsed !== null
            ? formatNumber(parsed, {
                fractionDigits: fractionDigitsFromStep(step),
              })
            : ""
        }
      />
    )
  }

  return (
    <Input
      {...props}
      nativeInputProps={{
        inputMode: "decimal",
        value: value ?? "",
        onChange: onChange
          ? (e) => {
              const next = e.target.value
              onChange(next === "" ? undefined : next)
            }
          : undefined,
      }}
    />
  )
}
