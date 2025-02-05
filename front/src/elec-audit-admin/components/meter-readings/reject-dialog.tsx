import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../../api"
import ApplicationStatus from "elec/components/application-status"
import { ElecMeterReadingsApplication } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import Checkbox from "common/components/checkbox"
import { useState } from "react"
export type ApplicationDialogProps = {
  application: ElecMeterReadingsApplication
  onClose: () => void
  onRejected: () => void
  forceRejection: boolean
}

export const MeterReadingsApplicationRejectDialog = ({
  application,
  onClose,
  forceRejection,
  onRejected,
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const [confirmCheckbox, setConfirmCheckbox] = useState(false)

  const rejectMeterReadingsApplication = useMutation(
    api.rejectMeterReadingsApplication,
    {
      invalidates: [
        "audit-charge-points-applications",
        "elec-admin-audit-snapshot",
        `nav-stats-${entity.id}`,
      ],
      onSuccess() {
        onClose()
        onRejected()
        notify(
          t("Les relevés T{{quarter}} {{year}} ont été refusés !", {
            quarter: application.quarter,
            year: application.year,
          }),
          { variant: "success" }
        )
      },
      onError(err) {
        notifyError(
          err,
          t("Impossible de valider les relevés de points de recharge.")
        )
      },
    }
  )

  const rejectApplication = () => {
    rejectMeterReadingsApplication.execute(
      entity.id,
      application.id,
      forceRejection
    )
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <ApplicationStatus status={application.status} big />
        <h1>{t("Refuser les relevés")}</h1>
      </header>

      <main>
        <section>
          <p style={{ textAlign: "left" }}>
            <Trans
              values={{
                quarter: application.quarter,
                year: application.year,
              }}
              count={application.charge_point_count}
              defaults="Refuser le relevé des <b>{{count}}</b> points de recharge pour T{{quarter}} {{year}} ?"
            />
          </p>

          <p>
            <Checkbox
              value={confirmCheckbox}
              onChange={setConfirmCheckbox}
              label={t(
                " Je confirme avoir partagé le motif de mon refus à l'aménageur par e-mail."
              )}
            />
          </p>
        </section>
      </main>

      <footer>
        <Button
          icon={Check}
          label={
            forceRejection
              ? t("Refuser la demande sans audit")
              : t("Refuser la demande")
          }
          variant="danger"
          action={rejectApplication}
          loading={rejectMeterReadingsApplication.loading}
          disabled={!confirmCheckbox}
        />
      </footer>
    </Dialog>
  )
}

export default MeterReadingsApplicationRejectDialog
