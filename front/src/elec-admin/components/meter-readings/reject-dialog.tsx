import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "elec-admin/api"
import ApplicationStatus from "elec/components/meter-readings/application-status"
import { ElecMeterReadingsApplication, ElecMeterReadingsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
export type ApplicationDialogProps = {
  application: ElecMeterReadingsApplication
  onClose: () => void
  companyId: number
}

export const MeterReadingsApplicationRejectDialog = ({
  application,
  onClose,
  companyId,
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const rejectMeterReadingsApplication = useMutation(api.rejectMeterReadingsApplication, {
    invalidates: ["meter-readings-applications"],
    onSuccess() {
      onClose()
      notify(t("Les relevés pour les {{count}} points de recharge ont été refusés !", { count: application.charging_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible de refuser les relevés de points de recharge"))
    },
  })

  const rejectApplication = () => {
    rejectMeterReadingsApplication.execute(entity.id, companyId, application.id)
  }

  const quarterString = t("T{{quarter}} {{year}}", { quarter: application.quarter, year: application.year })

  return (
    <Dialog onClose={onClose}>
      <header>
        <ApplicationStatus status={application.status} big />

        <h1>{t("Refuser les relevés trimestriels")}</h1>
      </header>

      <main>

        <section>
          <p style={{ textAlign: 'left' }}>
            <Trans
              values={{
                applicationDate: formatDate(application.application_date),
                quarterString: quarterString

              }}
              count={application.charging_point_count}
              defaults="<b>{{count}}</b> relevés de points de recharge importés le <b>{{applicationDate}}</b> pour le {{quarterString}}." />
          </p>
          <p>
            <Trans>Voulez-vous refuser ces relevés trimestriels ? Cela entraînera la suppression du fichier sur CarbuRe.</Trans>
          </p>
        </section>
      </main>

      <footer>

        {application.status === ElecMeterReadingsApplicationStatus.Pending && (
          <>
            <Button icon={Check} label={t("Refuser")} variant="danger" action={rejectApplication} loading={rejectMeterReadingsApplication.loading} />
          </>
        )}
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default MeterReadingsApplicationRejectDialog


