import { useTranslation } from "react-i18next"
import { UserRightRequest } from "common/types"
import { usePortal } from "common/components/portal"
import { Button } from "common/components/button2"
import { Confirm } from "common/components/dialog2"

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

  const user = request.user[0]

  return (
    <Button
      captive
      iconId="ri-close-line"
      title={t("Révoquer")}
      priority="tertiary no outline"
      onClick={() =>
        portal((close) => (
          <Confirm
            title={t("Révoquer les droits d'un utilisateur")}
            description={t("Voulez vous révoquer les droits d'accès de {{user}} à votre société ?", { user })} // prettier-ignore
            confirm={t("Révoquer")}
            icon="ri-close-line"
            customVariant="danger"
            onConfirm={() => Promise.resolve(onRevokeUser())}
            onClose={close}
            hideCancel
          />
        ))
      }
    />
  )
}
