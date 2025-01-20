import { forwardRef } from "react"
import { Input, InputProps } from "../input"

export type NumberInputProps = InputProps & {
  min?: number
  max?: number
  step?: number
  value?: number
  onChange?: (value: number | undefined) => void
}

export const NumberInput = forwardRef<HTMLInputElement, NumberInputProps>(
  ({ value, onChange, min, max, step, ...props }, ref) => {
    return (
      <Input
        {...props}
        type={props.readOnly ? "text" : "number"}
        ref={ref}
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
)
