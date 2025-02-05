import { Input, InputProps } from "../input"
export type TextInputProps = InputProps & {
  value?: string
  autoComplete?: boolean
  onChange?: (value: string | undefined) => void
}

export const TextInput = ({
  value,
  onChange,
  autoComplete,
  ...props
}: TextInputProps) => {
  return (
    <Input
      {...props}
      nativeInputProps={{
        value,
        onChange: onChange ? (e) => onChange(e.target.value) : undefined,
        autoComplete: autoComplete ? "on" : undefined,
      }}
    />
  )
}
