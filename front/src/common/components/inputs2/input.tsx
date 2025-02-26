import { InputProps as InputPropsDSFR } from "@codegouvfr/react-dsfr/Input"
import { RefObject } from "react"
import { BaseInput, ExtendedInputProps } from "./base-input"

// Props to be exposed to all inputs (text/number/date etc...)
export type InputProps = Omit<
  InputPropsDSFR,
  "nativeInputProps" | "textArea" | "nativeTextAreaProps" | "label"
> &
  ExtendedInputProps & {
    inputRef?: React.RefObject<HTMLInputElement>
    label?: InputPropsDSFR["label"] // By default, the label is required in the DSFR
  }

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
  readOnly,
  inputRef,
  required,
  label,
  ...props
}: Omit<InputPropsDSFR.RegularInput, "label"> &
  ExtendedInputProps & {
    inputRef?: React.RefObject<HTMLInputElement>
    label?: InputPropsDSFR["label"] // By default, the label is required in the DSFR
  }) => {
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
        readOnly,
        required,
        ref: inputRef as RefObject<HTMLInputElement>,
      }}
      textArea={false}
      label={label ?? ""}
      readOnly={readOnly}
    />
  )
}
