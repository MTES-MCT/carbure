import { Form, useForm } from "common/components/form"
import { TextInput } from "common/components/input"
import { usePortal } from "common/components/portal"
import { useUser } from "common/hooks/user"
import { useTranslation } from "react-i18next"
import { useMutation } from "common/hooks/async"
import * as api from "../../../api"
import { useNotify } from "common/components/notifications"
import { EmailConfirmationModal } from "./email-confirmation-modal"
import { Check } from "common/components/icons"
import Button from "common/components/button"

export interface ChangeEmailFormProps {
  onEmailChange: (email: string) => void
}

export const ChangeEmailForm = ({ onEmailChange }: ChangeEmailFormProps) => {
  const portal = usePortal()
  const user = useUser()
  const { t } = useTranslation()
  const notify = useNotify()
  const { value, bind, setValue } = useForm<{
    email: string
    newEmail: string | undefined
    password: string | undefined
  }>({
    email: user.email,
    newEmail: "",
    password: "",
  })

  const handleSave = () => {
    if (value.newEmail && value.password) {
      requestEmailChangeMutation.execute(value.newEmail, value.password)
    }
  }

  const requestEmailChangeMutation = useMutation(api.requestEmailChange, {
    onSuccess: () => {
      portal((close) => (
        <EmailConfirmationModal
          newEmail={value.newEmail!}
          onClose={close}
          onSuccess={() => {
            onEmailChange(value.newEmail || "")
            setValue({
              email: value.newEmail || "",
              newEmail: "",
              password: "",
            })
          }}
        />
      ))
    },
    onError: (error: any) => {
      let errorData
      try {
        errorData = JSON.parse(error.message)
      } catch {
        errorData = error.response?.data || error
      }

      if (errorData?.message === "INVALID_DATA" && errorData?.errors) {
        const { errors } = errorData

        if (errors.new_email?.includes("EMAIL_ALREADY_USED")) {
          notify(
            t("Cette adresse email est déjà utilisée par un autre compte."),
            { variant: "danger" }
          )
        }
        if (errors.password?.includes("WRONG_PASSWORD")) {
          notify(t("Le mot de passe saisi est incorrect."), {
            variant: "danger",
          })
        }
      } else {
        notify(t("Erreur lors de la demande de changement d'email."), {
          variant: "danger",
        })
      }
    },
  })

  return (
    <Form id="update-email-form" onSubmit={handleSave}>
      <TextInput
        readOnly
        label={t("Adresse email actuelle")}
        type="email"
        value={value.email}
      />

      <TextInput
        label={t("Nouvelle adresse email")}
        type="email"
        required
        {...bind("newEmail")}
      />

      <TextInput
        label={t("Saisissez votre mot de passe pour confirmer")}
        type="password"
        required
        {...bind("password")}
      />
      <Button
        variant="primary"
        icon={Check}
        label={t("Enregistrer mon email")}
        submit="update-email-form"
        loading={requestEmailChangeMutation.loading}
        disabled={!value.newEmail || !value.password}
        asideX
      />
    </Form>
  )
}
