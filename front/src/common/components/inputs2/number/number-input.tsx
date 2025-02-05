import { Input, InputProps } from "../input"

export type NumberInputProps = InputProps & {
  label?: string
  min?: number
  max?: number
  step?: number
  value?: number
  onChange?: (value: number | undefined) => void
}

export const NumberInput = ({
  label,
  value,
  onChange,
  min,
  max,
  step,
  ...props
}: NumberInputProps) => {
  return (
    <Input
      {...props}
      label={label}
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
