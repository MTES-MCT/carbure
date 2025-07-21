import { Trans, useTranslation } from "react-i18next"
import { useState } from "react"
import { useUser } from "common/hooks/user"
import { useForm } from "common/components/form"
import { TextInput } from "common/components/input"
import { Button } from "common/components/button"
import { Edit, Cross } from "common/components/icons"
import { Panel } from "common/components/scaffold"
import { ChangePasswordForm } from "./change-password-form"
import { ChangeEmailForm } from "./change-email-form"

export const AccountAuthentication = () => {
  const { t } = useTranslation()
  const user = useUser()
  const [isEditing, setIsEditing] = useState(false)

  const { value, bind } = useForm({
    email: user.email,
    newEmail: "",
    password: "",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })

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
            // disabled={
            //   requestEmailChangeMutation.loading ||
            //   requestPasswordChangeMutation.loading
            // }
          />
        )}
        {isEditing && (
          <Button
            asideX
            variant="secondary"
            icon={Cross}
            label={t("Annuler")}
            action={handleCancel}
            // disabled={
            //   requestEmailChangeMutation.loading ||
            //   requestPasswordChangeMutation.loading
            // }
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
        {!isEditing && (
          <TextInput
            readOnly
            label={t("Adresse email actuelle")}
            type="email"
            value={value.email}
            style={{ width: "100%" }}
          />
        )}
        {isEditing && (
          <>
            <ChangeEmailForm onEmailChange={() => setIsEditing(false)} />
            <ChangePasswordForm />
          </>
        )}
      </footer>
    </Panel>
  )
}
