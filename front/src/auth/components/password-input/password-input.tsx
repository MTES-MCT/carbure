import {
  PasswordInput as DsfrPasswordInput,
  PasswordInputProps as DsfrPasswordInputProps,
} from "@codegouvfr/react-dsfr/blocks/PasswordInput"
import { usePasswordValidation } from "./use-password-validation"

export type PasswordInputProps = Omit<
  DsfrPasswordInputProps,
  "nativeInputProps" | "label"
> & {
  label?: DsfrPasswordInputProps["label"]
  value?: string | null
  onChange?: (value: string | undefined) => void
  /**
   * When provided, the field validates that its value matches this one
   * (password confirmation) instead of checking the password rules.
   */
  confirm?: string | null
  required?: boolean
  autoFocus?: boolean
  name?: string
  autoComplete?: string
  nativeInputProps?: DsfrPasswordInputProps["nativeInputProps"]
}

/**
 * Wrapper around the DSFR PasswordInput exposing `value`/`onChange` directly
 * (the DSFR component only accepts them through `nativeInputProps`).
 *
 * Validation messages are built by `usePasswordValidation` and fed to the
 * DSFR `messages` field. An explicit `messages` prop still takes precedence.
 */
export const PasswordInput = ({
  label,
  value,
  onChange,
  confirm,
  required,
  autoFocus,
  name,
  autoComplete,
  messages,
  messagesHint,
  nativeInputProps,
  ...props
}: PasswordInputProps) => {
  const isConfirmation = confirm !== undefined
  const validation = usePasswordValidation(value, confirm)
  const computedMessages = isConfirmation
    ? validation.confirmationMessages
    : validation.messages

  return (
    <DsfrPasswordInput
      {...props}
      label={required ? <>{label} *</> : label}
      messages={messages ?? computedMessages}
      messagesHint={messagesHint ?? (isConfirmation ? "" : undefined)}
      nativeInputProps={{
        ...nativeInputProps,
        name,
        value: value ?? "",
        autoFocus,
        required,
        autoComplete,
        onChange: onChange ? (e) => onChange(e.target.value) : undefined,
      }}
    />
  )
}
