import { useTranslation } from "react-i18next"
import { Edit } from "common/components/icons"
import { UserRightRequest, UserRole } from "carbure/types"
import Button from "common/components/button"
import { usePortal } from "common/components/portal"
import { ChangeUserRoleDialog } from "./change-user-role-dialog"

export type ChangeUserRoleButtonProps = {
  onChangeUserRole: (role: UserRole) => void
  loading: boolean
  request: UserRightRequest
}

export const ChangeUserRoleButton = ({
  onChangeUserRole,
  loading,
  request,
}: ChangeUserRoleButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const handleSubmit = async (role: UserRole) => {
    onChangeUserRole(role)
  }

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
            loading={loading}
          />
        ))
      }
    />
  )
}
