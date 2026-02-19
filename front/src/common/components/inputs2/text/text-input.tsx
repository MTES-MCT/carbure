import { Input, InputProps } from "../input"
export type TextInputProps = InputProps & {
  value?: string | null
  autoComplete?: boolean
  onChange?: (value: string | undefined) => void
  onPaste?: (
    value: string | undefined,
    event: React.ClipboardEvent<HTMLInputElement>
  ) => void
}

export const TextInput = ({
  value,
  onChange,
  onPaste,
  autoComplete,
  ...props
}: TextInputProps) => {
  return (
    <Input
      {...props}
      nativeInputProps={{
        value: value ?? "",
        onChange: onChange ? (e) => onChange(e.target.value) : undefined,
        autoComplete: autoComplete ? "on" : "off",
        onPaste: onPaste
          ? (e) => onPaste(e.clipboardData.getData("text"), e)
          : undefined,
      }}
    />
  )
}
