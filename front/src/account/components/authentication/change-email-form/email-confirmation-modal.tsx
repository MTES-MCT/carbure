import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import * as api from "../../../api"
import Dialog from "common/components/dialog"
import Form from "common/components/form"
import { TextInput } from "common/components/input"
import Button from "common/components/button"
import { Check, Cross } from "common/components/icons"

interface EmailConfirmationModalProps {
  newEmail: string
  onClose: () => void
  onSuccess: () => void
}

export const EmailConfirmationModal = ({
  newEmail,
  onClose,
  onSuccess,
}: EmailConfirmationModalProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const [otpCode, setOtpCode] = useState("")

  const confirmEmailMutation = useMutation(api.confirmEmailChange, {
    invalidates: ["user-settings"],
    onSuccess: () => {
      notify(t("L'adresse email a été mise à jour avec succès !"), {
        variant: "success",
      })
      onSuccess()
      onClose()
    },
    onError: (error: any) => {
      let errorData
      try {
        errorData = JSON.parse(error.message)
      } catch {
        errorData = error.response?.data || error
      }

      if (errorData?.error) {
        const { error: errorCode } = errorData

        if (errorCode?.includes("INVALID_OTP")) {
          notify(t("Le code saisi est incorrect."), { variant: "danger" })
        } else if (errorCode?.includes("OTP_CODE_EXPIRED")) {
          notify(t("Le code a expiré. Veuillez refaire une demande."), {
            variant: "danger",
          })
        } else if (errorCode?.includes("NO_CHANGE_REQUEST")) {
          notify(
            t("Il n'y a pas de demande de changement pour l'email passé."),
            { variant: "danger" }
          )
        } else {
          notify(t("Erreur lors de la validation du code."), {
            variant: "danger",
          })
        }
      } else {
        notify(t("Erreur lors de la confirmation du changement d'email."), {
          variant: "danger",
        })
      }
    },
  })

  const handleConfirm = () => {
    if (otpCode.trim()) {
      confirmEmailMutation.execute(newEmail, otpCode.trim())
    }
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Confirmer le changement d'email")}</h1>
      </header>
      <main>
        <section>
          <p>
            {t(
              "Un code à 6 chiffres a été envoyé à l'adresse {{email}}. Veuillez le saisir dans le champ ci-dessous pour confirmer le changement d'email :",
              { email: newEmail }
            )}
          </p>
          <Form id="confirm-email-form" onSubmit={handleConfirm}>
            <TextInput
              label={t("Code de confirmation")}
              type="text"
              required
              value={otpCode}
              onChange={(val) => setOtpCode(val || "")}
              placeholder={t("Saisissez le code reçu par email")}
              style={{ width: "100%" }}
              autoFocus
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          variant="primary"
          icon={Check}
          label={t("Valider le changement")}
          submit="confirm-email-form"
          loading={confirmEmailMutation.loading}
          disabled={!otpCode.trim()}
        />
        <Button
          variant="secondary"
          icon={Cross}
          label={t("Annuler")}
          action={onClose}
          disabled={confirmEmailMutation.loading}
        />
      </footer>
    </Dialog>
  )
}
