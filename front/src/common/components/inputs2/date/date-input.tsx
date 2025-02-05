import { Input, InputProps } from "../input"

export type DateInputProps = InputProps & {
  label?: string
  value?: string
  onChange?: (value: string | undefined) => void
}

export const DateInput = ({
  label,
  value,
  onChange,
  ...props
}: DateInputProps) => {
  return (
    <Input
      {...props}
      label={label}
      nativeInputProps={{
        value,
        onChange: onChange ? (e) => onChange(e.target.value) : undefined,
      }}
    />
  )
}
