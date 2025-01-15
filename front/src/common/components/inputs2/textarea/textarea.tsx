import { BaseInput, ExtendedInputProps } from "../base-input"
import { InputProps as InputPropsDSFR } from "@codegouvfr/react-dsfr/Input"

export type TextAreaProps = {
  rows?: number
  cols?: number
  maxLength?: number
  value: string | undefined
  onChange: (value: string | undefined) => void
} & ExtendedInputProps &
  InputPropsDSFR.TextArea & { inputRef?: React.RefObject<HTMLTextAreaElement> }

export const TextArea = ({
  rows,
  cols,
  name,
  placeholder,
  value,
  autoFocus,
  onChange,
  maxLength,
  disabled,
  readOnly,
  required,
  inputRef,
  ...props
}: TextAreaProps) => (
  <BaseInput
    {...props}
    textArea
    nativeTextAreaProps={{
      autoFocus,
      maxLength,
      rows,
      cols,
      name,
      placeholder,
      value: value ?? "",
      onChange: (e) => onChange(e.target.value),
      disabled,
      readOnly,
      required,
      style: {
        resize: "none",
        minHeight: "96px",
      },
      ref: inputRef,
    }}
  />
)
