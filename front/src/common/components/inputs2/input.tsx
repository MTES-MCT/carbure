import { InputProps as InputPropsDSFR } from "@codegouvfr/react-dsfr/Input"
import { forwardRef } from "react"
import { BaseInput, ExtendedInputProps } from "./base-input"

// Props to be exposed to all inputs (text/number/date etc...)
export type InputProps = Omit<
  InputPropsDSFR,
  "nativeInputProps" | "textArea" | "nativeTextAreaProps"
> &
  ExtendedInputProps

/**
 * Base component for creating TextInput/NumberInput/DateInput etc...
 * It simplifies the way props are passed to the input
 */
export const Input = forwardRef<
  HTMLDivElement,
  InputPropsDSFR.RegularInput & ExtendedInputProps
>(
  (
    {
      autoFocus,
      name,
      pattern,
      placeholder,
      type,
      nativeInputProps,
      readOnly,
      ...props
    },
    ref
  ) => {
    return (
      <BaseInput
        {...props}
        ref={ref}
        nativeInputProps={{
          ...nativeInputProps,
          autoFocus,
          name,
          pattern,
          placeholder,
          type,
          readOnly,
        }}
        textArea={false}
      />
    )
  }
)
