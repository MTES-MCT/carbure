import { useForm } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { Form } from "common/components/form2"
import { useMutation } from "common/hooks/async"
import * as api from "../../api"
import { useNotify } from "common/components/notifications"
import { EditableCard } from "common/molecules/editable-card"

export const ChangePasswordForm = () => {
  const notify = useNotify()
  const { t } = useTranslation()
  const { value, bind, setValue } = useForm<{
    currentPassword: string | undefined
    newPassword: string | undefined
    confirmPassword: string | undefined
  }>({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })

  const requestPasswordChangeMutation = useMutation(api.requestPasswordChange, {
    onSuccess: () => {
      notify(t("Votre mot de passe a été modifié avec succès !"), {
        variant: "success",
      })
      setValue({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      })
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

        if (errors.current_password?.includes("WRONG_CURRENT_PASSWORD")) {
          notify(t("Le mot de passe actuel saisi est incorrect."), {
            variant: "danger",
          })
        }
        if (errors.current_password?.includes("PASSWORDS_MATCH")) {
          notify(t("Le mot de passe actuel et le nouveau sont identiques."), {
            variant: "danger",
          })
        }
        if (
          errors.confirm_new_password?.includes("CONFIRM_PASSWORD_MISMATCH")
        ) {
          notify(t("Les mots de passe ne correspondent pas."), {
            variant: "danger",
          })
        }
        if (errors.new_password) {
          errors.new_password.forEach((err: string) => {
            notify(t(err), { variant: "danger" })
          })
        }
      } else {
        notify(t("Erreur lors de la modification du mot de passe."), {
          variant: "danger",
        })
      }
    },
  })

  const handlePasswordChange = () => {
    if (value.currentPassword && value.newPassword && value.confirmPassword) {
      requestPasswordChangeMutation.execute(
        value.currentPassword,
        value.newPassword,
        value.confirmPassword
      )
    }
  }
  return (
    <EditableCard title={t("Mot de passe")} headerActions={null}>
      <Form onSubmit={handlePasswordChange}>
        <TextInput
          label={t("Mot de passe actuel")}
          type="password"
          required
          {...bind("currentPassword")}
          style={{ width: "100%" }}
        />
        <TextInput
          label={t("Nouveau mot de passe")}
          type="password"
          required
          {...bind("newPassword")}
          style={{ width: "100%" }}
        />
        <TextInput
          label={t("Confirmation du nouveau mot de passe")}
          type="password"
          required
          {...bind("confirmPassword")}
          style={{ width: "100%" }}
        />
        <Button
          iconId="ri-check-line"
          loading={requestPasswordChangeMutation.loading}
          disabled={
            !value.currentPassword ||
            !value.newPassword ||
            !value.confirmPassword
          }
          asideX
          type="submit"
        >
          {t("Enregistrer mon mot de passe")}
        </Button>
      </Form>
    </EditableCard>
  )
}
