import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "elec-admin/api"
import ApplicationStatus from "elec/components/charging-points/application-status"
import { ElecChargingPointsApplication, ElecChargingPointsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
export type ApplicationDialogProps = {
  application: ElecChargingPointsApplication
  onClose: () => void
  companyId: number
}

export const ChargingPointsApplicationAcceptDialog = ({
  application,
  onClose,
  companyId,
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const acceptChargingPointsApplication = useMutation(api.acceptChargingPointsApplication, {
    invalidates: ["charging-points-applications"],
    onSuccess() {
      onClose()
      notify(t("Les {{count}} points de recharge ont été acceptés !", { count: application.charging_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible d'accepter l'inscription des points de recharge"))
    },
  })


  const acceptApplication = () => {
    acceptChargingPointsApplication.execute(entity.id, companyId, application.id)
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
              count={application.charging_point_count}
              defaults="<b>{{count}}</b> points de recharge importés le <b>{{applicationDate}}</b>  ." />
          </p>
          <p>
            <Trans>Voulez-vous accepter cette demande ?</Trans>
          </p>
        </section>
      </main>

      <footer>

        {application.status === ElecChargingPointsApplicationStatus.Pending && (
          <>
            <Button icon={Check} label={t("Accepter la demande")} variant="success" action={acceptApplication} loading={acceptChargingPointsApplication.loading} />
          </>
        )}
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default ChargingPointsApplicationAcceptDialog


