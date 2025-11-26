import { InputProps as InputPropsDSFR } from "@codegouvfr/react-dsfr/Input"
import { RefObject } from "react"
import { BaseInput, ExtendedInputProps } from "./base-input"

type CommonInputProps = {
  inputRef?: React.RefObject<HTMLInputElement>
  label?: InputPropsDSFR["label"] // By default, the label is required in the DSFR
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void
}
// Props to be exposed to all inputs (text/number/date etc...)
export type InputProps = Omit<
  InputPropsDSFR,
  | "nativeInputProps"
  | "textArea"
  | "nativeTextAreaProps"
  | "label"
  | "nativeLabelProps"
> &
  ExtendedInputProps &
  CommonInputProps

/**
 * Base component for creating TextInput/NumberInput/DateInput etc...
 * It simplifies the way props are passed to the input
 */
export const Input = ({
  autoFocus,
  name,
  pattern,
  placeholder,
  type,
  nativeInputProps,
  inputRef,
  label,
  onKeyDown,
  onBlur,
  ...props
}: Omit<InputPropsDSFR.RegularInput, "label"> &
  ExtendedInputProps &
  CommonInputProps) => {
  return (
    <BaseInput
      {...props}
      nativeInputProps={{
        ...nativeInputProps,
        autoFocus,
        name,
        pattern,
        placeholder,
        type,
        readOnly: props.readOnly,
        required: props.required,
        ref: inputRef as RefObject<HTMLInputElement>,
        onKeyDown,
        onBlur,
      }}
      textArea={false}
      label={label ?? ""}
    />
  )
}
