import useEntity from "carbure/hooks/entity"
import { Confirm } from "common/components/dialog"
import { Check } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { PortalInstance } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { DoubleCountingApplicationDetails } from "double-counting/types"
import { useTranslation } from "react-i18next"
import * as api from "../../../api"

type ApplicationDetailsDialogValidateQuotasProps = {
  application: DoubleCountingApplicationDetails
  onClose: PortalInstance["close"]
}
const ApplicationDetailsDialogValidateQuotas = ({
  application,
  onClose,
}: ApplicationDetailsDialogValidateQuotasProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const approveApplication = useMutation(api.approveDoubleCountingApplication, {
    invalidates: ["dc-applications", "dc-snapshot", "dc-agreements"],
    onSuccess: () => {
      notify(t("Les quotas ont bien été validés."), { variant: "success" })
      onClose()
    },
  })

  return (
    <Confirm
      variant="primary"
      title={t("Valider les quotas")}
      description={
        <>
          <p>{t("Voulez-vous vraiment valider les quotas ?")}</p>
          <p>
            {t(
              "Une fois accepté, vous retrouverez l'agrément correspondant dans la liste des agréments actifs"
            )}
          </p>
        </>
      }
      confirm={t("Valider")}
      icon={Check}
      onClose={onClose}
      onConfirm={async () => {
        if (application) {
          await approveApplication.execute(entity.id, application.id)
        }
      }}
    />
  )
}

export default ApplicationDetailsDialogValidateQuotas
