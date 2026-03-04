import { useTranslation } from "react-i18next"
import { UserRightRequest } from "common/types"
import { usePortal } from "common/components/portal"
import { Button } from "common/components/button2"
import { Confirm } from "common/components/dialog2"

type RejectUserButtonProps = {
  onRejectUser: () => void
  request: UserRightRequest
}

export const RejectUserButton = ({
  request,
  onRejectUser,
}: RejectUserButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const user = request.user.email

  return (
    <Button
      captive
      iconId="ri-close-line"
      title={t("Refuser")}
      priority="tertiary no outline"
      onClick={() =>
        portal((close) => (
          <Confirm
            title={t("Refuser un utilisateur")}
            description={t("Voulez vous refuser l'accès à votre société à {{user}} ?", { user })} // prettier-ignore
            confirm={t("Refuser")}
            icon="ri-close-line"
            customVariant="danger"
            onConfirm={() => Promise.resolve(onRejectUser())}
            onClose={close}
            hideCancel
          />
        ))
      }
    />
  )
}
