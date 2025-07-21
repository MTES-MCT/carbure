import { Trans, useTranslation } from "react-i18next"
import { useState } from "react"
import { useUser } from "common/hooks/user"
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

  const handleCancel = () => {
    setIsEditing(false)
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
          />
        )}
        {isEditing && (
          <Button
            asideX
            variant="secondary"
            icon={Cross}
            label={t("Annuler")}
            action={handleCancel}
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
            value={user.email}
            style={{ width: "100%" }}
          />
        )}
        {isEditing && (
          <>
            <ChangeEmailForm onEmailChange={() => setIsEditing(false)} />
            <ChangePasswordForm onPasswordChange={() => setIsEditing(false)} />
          </>
        )}
      </footer>
    </Panel>
  )
}
