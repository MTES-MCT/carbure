import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Cross, Download, Return } from "common/components/icons"
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

export const ChargingPointsApplicationDetailsDialog = ({
  application,
  onClose,
  companyId,
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const downloadChargingPointsApplication = () => {
    return api.downloadChargingPointsApplicationDetails(entity.id, companyId, application.id)
  }

  const acceptChargingPointsApplication = useMutation(api.acceptChargingPointsApplication, {
    invalidates: ["charging-points-applications"],
    onSuccess() {
      onClose()
      notify(t("Les {{count}} points de recharge ont été acceptés !", { count: application.charging_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible d'accepter les points de recharge"))
    },
  })

  const rejectChargingPointsApplication = useMutation(api.rejectChargingPointsApplication, {
    invalidates: ["charging-points-applications"],
    onSuccess() {
      onClose()
      notify(t("La demande d'inscription pour les {{count}} points de recharge a été refusée !", { count: application.charging_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible de refuser les points de recharge"))
    },
  })

  const rejectApplication = () => {
    rejectChargingPointsApplication.execute(entity.id, companyId, application.id)
  }

  const acceptApplication = () => {
    acceptChargingPointsApplication.execute(entity.id, companyId, application.id)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <ApplicationStatus status={application.status} big />

        <h1>{t("Inscription de points de recharge")}</h1>
      </header>

      <main>

        <section>
          <p style={{ textAlign: 'left' }}>
            <Trans
              values={{
                applicationDate: formatDate(application.application_date),
              }}
              count={application.charging_point_count}
              defaults="La demande d'inscription a été faite le <b>{{applicationDate}}</b> pour <b>{{count}} points de recharge</b>." />
          </p>

          <p>
            <Button icon={Download} label={t("Exporter les points de recharge")} variant="secondary" action={downloadChargingPointsApplication} />
          </p>
          {!entity.isAdmin && application.status === ElecChargingPointsApplicationStatus.Pending && (
            <p><i>
              {t("En attente de validation de la DGEC.")}
            </i></p>
          )}
        </section>
      </main>

      <footer>

        {entity.isAdmin && application.status === ElecChargingPointsApplicationStatus.Pending && (
          <>
            <Button icon={Check} label={t("Valider l'inscription")} variant="success" action={acceptApplication} loading={acceptChargingPointsApplication.loading} />
            <Button icon={Cross} label={t("Refuser")} variant="danger" action={rejectApplication} loading={rejectChargingPointsApplication.loading} />
          </>
        )}
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default ChargingPointsApplicationDetailsDialog


