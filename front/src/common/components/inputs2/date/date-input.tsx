import { Input, InputProps } from "../input"

export type DateInputProps = InputProps & {
  value?: string
  onChange?: (value: string | undefined) => void
  min?: string
  max?: string
}

export const DateInput = ({
  value,
  onChange,
  min,
  max,
  ...props
}: DateInputProps) => {
  return (
    <Input
      {...props}
      type="date"
      nativeInputProps={{
        value: value ?? "",
        onChange: onChange ? (e) => onChange(e.target.value) : undefined,
        min,
        max,
      }}
    />
  )
}
