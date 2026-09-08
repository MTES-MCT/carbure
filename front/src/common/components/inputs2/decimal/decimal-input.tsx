import { NumberInput, NumberInputProps } from "../number/number-input"

export type DecimalInputProps = Omit<NumberInputProps, "value" | "onChange"> & {
  value?: string | null
  onChange?: (value: string | undefined) => void
}

function toNumber(value: string | null | undefined): number | null {
  if (value === null || value === undefined || value === "") return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

export const DecimalInput = ({
  value,
  onChange,
  ...props
}: DecimalInputProps) => {
  return (
    <NumberInput
      {...props}
      value={toNumber(value)}
      onChange={
        onChange
          ? (next) => onChange(next === undefined ? undefined : String(next))
          : undefined
      }
    />
  )
}
