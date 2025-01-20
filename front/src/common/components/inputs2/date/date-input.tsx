import { forwardRef } from "react"
import { Input, InputProps } from "../input"

export type DateInputProps = InputProps & {
  value?: string
  onChange?: (value: string | undefined) => void
}

export const DateInput = forwardRef<HTMLInputElement, DateInputProps>(
  ({ value, onChange, ...props }, ref) => {
    return (
      <Input
        {...props}
        ref={ref}
        nativeInputProps={{
          value,
          onChange: onChange ? (e) => onChange(e.target.value) : undefined,
        }}
      />
    )
  }
)
