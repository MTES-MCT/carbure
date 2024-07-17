import { useTranslation } from "react-i18next"
import Dialog from "common/components/dialog"
import { Edit, Return } from "common/components/icons"
import { UserRightRequest, UserRole } from "carbure/types"
import Button from "common/components/button"
import { type PortalInstance } from "common/components/portal"
import { Form } from "common/components/form"
import { RadioGroup } from "common/components/radio"
import { useState } from "react"
import useEntity from "carbure/hooks/entity"

type ChangeUserRoleDialogProps = {
  request: UserRightRequest
  onSubmit: (role: UserRole) => Promise<unknown>
  onClose: PortalInstance["close"]
  loading: boolean
}

export const ChangeUserRoleDialog = ({
  request,
  onSubmit,
  onClose,
  loading,
}: ChangeUserRoleDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const [role, setRole] = useState<UserRole | undefined>(request.role)
  const userEmail = request.user[0]

  const handleSubmit = async () => {
    if (role) {
      await onSubmit(role)
      onClose()
    }
  }
  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Modifier le rôle")}</h1>
      </header>
      <main>
        <section>
          {t("Modifier le rôle de l'utilisateur {{userEmail}} ?", {
            userEmail,
          })}
        </section>
        <section>
          <Form id="access-right" onSubmit={handleSubmit}>
            <RadioGroup
              label={t("Rôle")}
              name="role"
              value={role}
              onChange={setRole}
              options={[
                {
                  value: UserRole.ReadOnly,
                  label: t("Lecture seule"),
                },
                {
                  value: UserRole.ReadWrite,
                  label: t("Lecture/écriture"),
                },
                {
                  value: UserRole.Admin,
                  label: t("Administration (contrôle complet de la société sur CarbuRe)"), // prettier-ignore
                },
              ]}
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          variant="primary"
          loading={loading}
          icon={Edit}
          label={t("Modifier le rôle")}
          disabled={!entity || !role}
          submit="access-right"
        />
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}
