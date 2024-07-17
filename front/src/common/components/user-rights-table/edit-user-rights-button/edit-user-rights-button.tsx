import { useTranslation } from "react-i18next"
import Dialog from "common/components/dialog"
import { Edit, Return } from "common/components/icons"
import { UserRightRequest, UserRole } from "carbure/types"
import Button from "common/components/button"
import { PortalInstance, usePortal } from "common/components/portal"
import { Form } from "common/components/form"
import { RadioGroup } from "common/components/radio"
import { useState } from "react"
import useEntity from "carbure/hooks/entity"

type EditUserRightsButtonProps = {
  onEditUserRight: (role: UserRole) => void
  loading: boolean
  request: UserRightRequest
}

export const EditUserRightsButton = ({
  onEditUserRight,
  loading,
  request,
}: EditUserRightsButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()
  const [role, setRole] = useState<UserRole | undefined>(request.role)
  const userEmail = request.user[0]

  const handleSubmit = (onClose: PortalInstance["close"]) => async () => {
    if (role) {
      await onEditUserRight(role)
    }
    onClose()
  }

  return (
    <Button
      captive
      variant="icon"
      icon={Edit}
      title={t("Modifier le rôle")}
      action={() =>
        portal((close) => (
          <Dialog onClose={close}>
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
                <Form id="access-right" onSubmit={handleSubmit(close)}>
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
                        label: t("Lecture/écriture)"),
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
              <Button asideX icon={Return} action={close} label={t("Retour")} />
            </footer>
          </Dialog>
        ))
      }
    />
  )
}
