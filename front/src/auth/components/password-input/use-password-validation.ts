import { useTranslation } from "react-i18next"
import type { PasswordInputProps } from "@codegouvfr/react-dsfr/blocks/PasswordInput"

type PasswordMessage = NonNullable<PasswordInputProps["messages"]>[number]

type PasswordRule = {
  label: string
  test: (value: string) => boolean
}

const MIN_LENGTH = 12

/**
 * Build the message severity following the DSFR pattern:
 * - empty field -> neutral "info"
 * - filled field -> "valid" when the rule passes, "error" otherwise
 */
const getSeverity = (
  value: string,
  passed: boolean
): PasswordMessage["severity"] => {
  if (value === "") return "info"
  return passed ? "valid" : "error"
}

/**
 * Validate a password against the rules enforced by the Django backend
 * (see AUTH_PASSWORD_VALIDATORS). Only the rules checkable client-side are
 * surfaced here; the backend remains the source of truth.
 *
 * When a confirmation value is provided, it also checks that both fields match.
 */
export const usePasswordValidation = (
  password: string | undefined | null,
  confirmation?: string | undefined | null
) => {
  const { t } = useTranslation()
  const value = password ?? ""

  const rules: PasswordRule[] = [
    {
      label: t("12 caractères minimum"),
      test: (v) => v.length >= MIN_LENGTH,
    },
    {
      label: t("Au moins une lettre"),
      test: (v) => /\p{L}/u.test(v),
    },
  ]

  const messages: PasswordMessage[] = rules.map((rule) => ({
    message: rule.label,
    severity: getSeverity(value, rule.test(value)),
  }))

  const isPasswordValid = rules.every((rule) => rule.test(value))

  const hasConfirmation = confirmation !== undefined && confirmation !== null
  const confirmationValue = confirmation ?? ""
  const isMatching = value === confirmationValue

  const confirmationMessages: PasswordMessage[] = hasConfirmation
    ? [
        {
          message: t("Les deux mots de passe doivent être identiques"),
          severity: getSeverity(confirmationValue, isMatching),
        },
      ]
    : []

  const isValid = isPasswordValid && (!hasConfirmation || isMatching)

  return {
    messages,
    confirmationMessages,
    isMatching,
    isValid,
  }
}
