import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "../../api"
import ApplicationStatus from "elec/components/charge-points/application-status"
import { ElecChargePointsApplication, ElecChargePointsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
export type ApplicationDialogProps = {
  application: ElecChargePointsApplication
  onClose: () => void,
  forceValidation: boolean
}

export const ChargePointsApplicationAcceptDialog = ({
  application,
  onClose,
  forceValidation
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const acceptChargePointsApplication = useMutation(api.acceptChargePointsApplication, {
    invalidates: ["audit-charge-points-applications"],
    onSuccess() {
      onClose()
      notify(t("Les {{count}} points de recharge ont été acceptés !", { count: application.charge_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible d'accepter l'inscription des points de recharge"))
    },
  })


  const acceptApplication = () => {
    acceptChargePointsApplication.execute(entity.id, application.id, forceValidation)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <ApplicationStatus status={application.status} big />

        <h1>{t("Accepter les points de recharge")}</h1>
      </header>

      <main>

        <section>
          <p style={{ textAlign: 'left' }}>
            <Trans
              values={{
                applicationDate: formatDate(application.application_date),
              }}
              count={application.charge_point_count}
              defaults="<b>{{count}}</b> points de recharge importés le <b>{{applicationDate}}</b>  ." />
          </p>
          <p>
            <Trans>Voulez-vous accepter cette demande ?</Trans>
          </p>
        </section>
      </main>

      <footer>



        <Button icon={Check} label={forceValidation ? t("Accepter la demande sans audit") : t("Accepter la demande")} variant="success" action={() => acceptApplication} loading={acceptChargePointsApplication.loading} />



        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default ChargePointsApplicationAcceptDialog


