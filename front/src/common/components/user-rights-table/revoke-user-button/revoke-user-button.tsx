import { useTranslation } from "react-i18next"
import { UserRightRequest } from "carbure/types"
import { usePortal } from "common/components/portal"
import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import { Check, Cross } from "common/components/icons"
import { Confirm } from "common/components/dialog"

type RevokeUserButtonProps = {
  onRevokeUser: () => void
  request: UserRightRequest
}
export const RevokeUserButton = ({
  request,
  onRevokeUser,
}: RevokeUserButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const user = request.user[0]

  return (
    <Button
      captive
      variant="icon"
      icon={Cross}
      title={t("Révoquer")}
      action={() =>
        portal((close) => (
          <Confirm
            title={t("Révoquer les droits d'un utilisateur")}
            description={t("Voulez vous révoquer les droits d'accès de {{user}} à votre société ?", { user })} // prettier-ignore
            confirm={t("Révoquer")}
            icon={Cross}
            variant="danger"
            onConfirm={() => Promise.resolve(onRevokeUser())}
            onClose={close}
          />
        ))
      }
    />
  )
}
