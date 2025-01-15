import { InputProps as InputPropsDSFR } from "@codegouvfr/react-dsfr/Input"
import { RefObject } from "react"
import { BaseInput, ExtendedInputProps } from "./base-input"

// Props to be exposed to all inputs (text/number/date etc...)
export type InputProps = Omit<
  InputPropsDSFR,
  "nativeInputProps" | "textArea" | "nativeTextAreaProps"
> &
  ExtendedInputProps & {
    inputRef?: React.RefObject<HTMLInputElement>
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
  ...props
}: InputPropsDSFR.RegularInput &
  ExtendedInputProps & { inputRef?: React.RefObject<HTMLInputElement> }) => {
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
        ref: inputRef as RefObject<HTMLInputElement>,
      }}
      textArea={false}
    />
  )
}
