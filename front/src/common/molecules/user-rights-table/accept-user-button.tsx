import { useTranslation } from "react-i18next"
import { UserRightRequest } from "common/types"
import { usePortal } from "common/components/portal"
import { Button } from "common/components/button2"
import { Confirm } from "common/components/dialog2"

type AcceptUserButtonProps = {
  onAcceptUser: () => void
  request: UserRightRequest
}
export const AcceptUserButton = ({
  request,
  onAcceptUser,
}: AcceptUserButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const user = request.user.email

  return (
    <Button
      captive
      iconId="ri-check-line"
      title={t("Accepter")}
      priority="tertiary no outline"
      onClick={() =>
        portal((close) => (
          <Confirm
            title={t("Accepter un utilisateur")}
            description={t("Voulez vous donner des droits d'accès à votre société à {{user}} ?", { user })} // prettier-ignore
            confirm={t("Accepter")}
            icon="ri-check-line"
            customVariant="success"
            onConfirm={() => Promise.resolve(onAcceptUser())}
            onClose={close}
            hideCancel
          />
        ))
      }
    />
  )
}
