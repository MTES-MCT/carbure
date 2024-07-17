import { useTranslation } from "react-i18next"
import { UserRightRequest } from "carbure/types"
import { usePortal } from "common/components/portal"
import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import { Check } from "common/components/icons"
import { Confirm } from "common/components/dialog"

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
  const entity = useEntity()

  const user = request.user[0]

  return (
    <Button
      captive
      variant="icon"
      icon={Check}
      title={t("Accepter")}
      action={() =>
        portal((close) => (
          <Confirm
            title={t("Accepter un utilisateur")}
            description={t("Voulez vous donner des droits d'accès à votre société à {{user}} ?", { user })} // prettier-ignore
            confirm={t("Accepter")}
            icon={Check}
            variant="success"
            onConfirm={() => Promise.resolve(onAcceptUser())}
            onClose={close}
          />
        ))
      }
    />
  )
}
