import { NumberInput, NumberInputProps } from "../number/number-input"

export type DecimalInputProps = Omit<
  NumberInputProps,
  "value" | "onChange" | "min" | "max"
> & {
  value?: string | null
  onChange?: (value: string | undefined) => void
  min?: string | number | null
  max?: string | number | null
}

function toNumber(value: string | number | null | undefined): number | null {
  if (value === null || value === undefined || value === "") return null
  const parsed = typeof value === "number" ? value : Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

export const DecimalInput = ({
  value,
  onChange,
  min,
  max,
  ...props
}: DecimalInputProps) => {
  return (
    <NumberInput
      {...props}
      min={toNumber(min) ?? undefined}
      max={toNumber(max) ?? undefined}
      value={toNumber(value)}
      onChange={
        onChange
          ? (next) => onChange(next === undefined ? undefined : String(next))
          : undefined
      }
    />
  )
}
