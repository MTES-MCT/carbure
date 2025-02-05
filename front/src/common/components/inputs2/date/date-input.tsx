import { Input, InputProps } from "../input"

export type DateInputProps = InputProps & {
  value?: string
  onChange?: (value: string | undefined) => void
}

export const DateInput = ({ value, onChange, ...props }: DateInputProps) => {
  return (
    <Input
      {...props}
      nativeInputProps={{
        value,
        onChange: onChange ? (e) => onChange(e.target.value) : undefined,
      }}
    />
  )
}
