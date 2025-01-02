import { forwardRef } from "react"
import { Input, InputProps } from "../input"

export type TextInputProps = InputProps & {
  value?: string
  autoComplete?: boolean
  onChange?: (value: string | undefined) => void
}

export const TextInput = forwardRef<HTMLInputElement, TextInputProps>(
  ({ value, onChange, autoComplete, ...props }, ref) => {
    return (
      <Input
        {...props}
        ref={ref}
        nativeInputProps={{
          value,
          onChange: onChange ? (e) => onChange(e.target.value) : undefined,
          autoComplete: autoComplete ? "on" : undefined,
        }}
      />
    )
  }
)
