import { useTranslation } from "react-i18next"
import { useState } from "react"
import { Edit, Return } from "common/components/icons"
import { UserRightRequest, UserRole } from "common/types"
import Button from "common/components/button"
import { usePortal } from "common/components/portal"
import Dialog from "common/components/dialog"
import { type PortalInstance } from "common/components/portal"
import { Form } from "common/components/form"
import { RadioGroup } from "common/components/radio"

import useEntity from "common/hooks/entity"
import { getUserRoleOptions } from "common/utils/normalizers"

type ChangeUserRoleDialogProps = {
  request: UserRightRequest
  onSubmit: (role: UserRole) => Promise<unknown>
  onClose: PortalInstance["close"]
}

export const ChangeUserRoleDialog = ({
  request,
  onSubmit,
  onClose,
}: ChangeUserRoleDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const [role, setRole] = useState<UserRole | undefined>(request.role)
  // Portal is not reactif, we can't pass loading state from parent mutation
  const [loading, setLoading] = useState(false)
  const userEmail = request.user[0]

  const handleSubmit = async () => {
    if (role) {
      try {
        setLoading(true)
        await onSubmit(role)
      } finally {
        setLoading(false)
      }

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
              options={getUserRoleOptions([
                UserRole.ReadOnly,
                UserRole.ReadWrite,
                UserRole.Admin,
              ])}
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

export type ChangeUserRoleButtonProps = {
  onChangeUserRole: (role: UserRole) => Promise<unknown>
  request: UserRightRequest
}

export const ChangeUserRoleButton = ({
  onChangeUserRole,
  request,
}: ChangeUserRoleButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const handleSubmit = (role: UserRole) => onChangeUserRole(role)

  return (
    <Button
      captive
      variant="icon"
      icon={Edit}
      title={t("Modifier le rôle")}
      action={() =>
        portal((close) => (
          <ChangeUserRoleDialog
            request={request}
            onSubmit={handleSubmit}
            onClose={close}
          />
        ))
      }
    />
  )
}
