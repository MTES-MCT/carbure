import { Trans, useTranslation } from "react-i18next"
import { useState } from "react"
import { useUser } from "common/hooks/user"
import { useMutation } from "common/hooks/async"
import Form, { useForm } from "common/components/form"
import { useNotify } from "common/components/notifications"
import { TextInput } from "common/components/input"
import { Button } from "common/components/button"
import { Edit, Check, Cross } from "common/components/icons"
import { Panel } from "common/components/scaffold"
import { usePortal } from "common/components/portal"
import Dialog from "common/components/dialog"
import * as api from "../api"

interface EmailConfirmationModalProps {
  newEmail: string
  onClose: () => void
  onSuccess: () => void
}

const EmailConfirmationModal = ({
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

export const AccountAuthentication = () => {
  const { t } = useTranslation()
  const user = useUser()
  const notify = useNotify()
  const portal = usePortal()
  const [isEditing, setIsEditing] = useState(false)

  const { value, bind } = useForm({
    email: user.email,
    newEmail: "",
    password: "",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })

  const requestEmailChangeMutation = useMutation(api.requestEmailChange, {
    onSuccess: () => {
      portal((close) => (
        <EmailConfirmationModal
          newEmail={value.newEmail!}
          onClose={close}
          onSuccess={() => {
            setIsEditing(false)
            bind("email").onChange(value.newEmail || "")
            bind("newEmail").onChange("")
            bind("password").onChange("")
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

  const requestPasswordChangeMutation = useMutation(api.requestPasswordChange, {
    onSuccess: () => {
      notify(t("Votre mot de passe a été modifié avec succès !"), {
        variant: "success",
      })
      setIsEditing(false)
      bind("currentPassword").onChange("")
      bind("newPassword").onChange("")
      bind("confirmPassword").onChange("")
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

  const handleSave = () => {
    if (value.newEmail && value.password) {
      requestEmailChangeMutation.execute(value.newEmail, value.password)
    }
  }

  const handlePasswordChange = () => {
    if (value.currentPassword && value.newPassword && value.confirmPassword) {
      if (value.newPassword !== value.confirmPassword) {
        notify(t("Les mots de passe ne correspondent pas."), {
          variant: "danger",
        })
        return
      }
      requestPasswordChangeMutation.execute(
        value.currentPassword,
        value.newPassword,
        value.confirmPassword
      )
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    bind("newEmail").onChange("")
    bind("password").onChange("")
    bind("currentPassword").onChange("")
    bind("newPassword").onChange("")
    bind("confirmPassword").onChange("")
  }

  return (
    <Panel>
      <header>
        <h1>
          <Trans>Identifiants</Trans>
        </h1>
        {!isEditing && user.email && (
          <Button
            asideX
            variant="primary"
            icon={Edit}
            label={t("Modifier mes identifiants")}
            action={() => setIsEditing(true)}
            disabled={
              requestEmailChangeMutation.loading ||
              requestPasswordChangeMutation.loading
            }
          />
        )}
        {isEditing && (
          <Button
            asideX
            variant="secondary"
            icon={Cross}
            label={t("Annuler")}
            action={handleCancel}
            disabled={
              requestEmailChangeMutation.loading ||
              requestPasswordChangeMutation.loading
            }
          />
        )}
      </header>

      <footer
        style={{
          flexDirection: "column",
          alignContent: "flex-end",
          alignItems: "normal",
        }}
      >
        <Form
          id="update-email-form"
          onSubmit={isEditing ? handleSave : undefined}
        >
          <TextInput
            readOnly={true}
            label={t("Adresse email actuelle")}
            type="email"
            value={value.email}
            style={{ width: "100%" }}
          />

          {isEditing && (
            <TextInput
              label={t("Nouvelle adresse email")}
              type="email"
              required
              value={value.newEmail}
              onChange={(val) => bind("newEmail").onChange(val || "")}
              error={bind("newEmail").error}
              style={{ width: "100%" }}
            />
          )}

          {isEditing && (
            <TextInput
              label={t("Saisissez votre mot de passe pour confirmer")}
              type="password"
              required
              value={value.password}
              onChange={(val) => bind("password").onChange(val || "")}
              error={bind("password").error}
              style={{ width: "100%" }}
            />
          )}
        </Form>

        {isEditing && (
          <div
            style={{
              display: "flex",
              gap: "var(--spacing-s)",
              marginTop: "var(--spacing-m)",
              justifyContent: "flex-end",
            }}
          >
            <Button
              variant="primary"
              icon={Check}
              label={t("Enregistrer mon email")}
              submit="update-email-form"
              loading={requestEmailChangeMutation.loading}
              disabled={!value.newEmail || !value.password}
            />
          </div>
        )}

        {isEditing && (
          <div style={{ marginTop: "var(--spacing-l)" }}>
            <Form id="update-password-form" onSubmit={handlePasswordChange}>
              <TextInput
                label={t("Mot de passe actuel")}
                type="password"
                required
                value={value.currentPassword}
                onChange={(val) => bind("currentPassword").onChange(val || "")}
                error={bind("currentPassword").error}
                style={{ width: "100%" }}
              />
              <TextInput
                label={t("Nouveau mot de passe")}
                type="password"
                required
                value={value.newPassword}
                onChange={(val) => bind("newPassword").onChange(val || "")}
                error={bind("newPassword").error}
                style={{ width: "100%" }}
              />
              <TextInput
                label={t("Confirmation du nouveau mot de passe")}
                type="password"
                required
                value={value.confirmPassword}
                onChange={(val) => bind("confirmPassword").onChange(val || "")}
                error={bind("confirmPassword").error}
                style={{ width: "100%" }}
              />
            </Form>
            <div
              style={{
                display: "flex",
                gap: "var(--spacing-s)",
                marginTop: "var(--spacing-m)",
                justifyContent: "flex-end",
              }}
            >
              <Button
                variant="primary"
                icon={Check}
                label={t("Enregistrer mon mot de passe")}
                submit="update-password-form"
                loading={requestPasswordChangeMutation.loading}
                disabled={
                  !value.currentPassword ||
                  !value.newPassword ||
                  !value.confirmPassword
                }
              />
            </div>
          </div>
        )}
      </footer>
    </Panel>
  )
}
