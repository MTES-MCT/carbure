import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "elec-admin/api"
import ApplicationStatus from "elec/components/charge-points/application-status"
import { ElecChargePointsApplication, ElecChargePointsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
export type ApplicationDialogProps = {
  application: ElecChargePointsApplication
  onClose: () => void
  companyId: number
}

export const ChargePointsApplicationRejectDialog = ({
  application,
  onClose,
  companyId,
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const rejectChargePointsApplication = useMutation(api.rejectChargePointsApplication, {
    invalidates: ["charge-points-applications"],
    onSuccess() {
      onClose()
      notify(t("La demande d'inscription pour les {{count}} points de recharge a été refusée !", { count: application.charge_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible de refuser l'inscription des points de recharge"))
    },
  })

  const rejectApplication = () => {
    rejectChargePointsApplication.execute(entity.id, companyId, application.id)
  }


  return (
    <Dialog onClose={onClose}>
      <header>
        <ApplicationStatus status={application.status} big />

        <h1>{t("Refuser les points de recharge")}</h1>
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
            <Trans>Voulez-vous refuser cette demande ?</Trans>
          </p>
        </section>
      </main>

      <footer>

        {application.status === ElecChargePointsApplicationStatus.Pending && (
          <>
            <Button icon={Check} label={t("Refuser la demande")} variant="danger" action={rejectApplication} loading={rejectChargePointsApplication.loading} />
          </>
        )}
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default ChargePointsApplicationRejectDialog


