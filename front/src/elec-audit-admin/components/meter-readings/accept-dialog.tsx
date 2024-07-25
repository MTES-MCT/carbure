import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, InfoCircle, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { formatDate, formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/application-status"
import { ElecMeterReadingsApplication } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../../api"
import Alert from "common/components/alert"
export type ApplicationDialogProps = {
  application: ElecMeterReadingsApplication
  onClose: () => void
  onValidated: () => void
  forceValidation: boolean
}

export const MeterReadingsApplicationAcceptDialog = ({
  application,
  onClose,
  onValidated,
  forceValidation,
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const acceptMeterReadingsApplication = useMutation(
    api.acceptMeterReadingsApplication,
    {
      invalidates: [
        "audit-meter-readings-applications",
        "elec-admin-audit-snapshot",
      ],
      onSuccess() {
        onClose()
        onValidated()
        notify(
          t("Les relevés T{{quarter}} {{year}} ont été acceptés !", {
            quarter: application.quarter,
            year: application.year,
          }),
          { variant: "success" }
        )
      },
      onError(err) {
        notifyError(
          err,
          t("Impossible d'accepter les relevés des points de recharge")
        )
      },
    }
  )

  const acceptApplication = (forceValidation: boolean) => {
    acceptMeterReadingsApplication.execute(
      entity.id,
      application.id,
      forceValidation
    )
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <ApplicationStatus status={application.status} big />

        <h1>{t("Accepter les relevés")}</h1>
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
              defaults="<b>{{count}}</b> relevés envoyés pour T{{quarter}} {{year}}.</b>"
            />
          </p>
          <p>
            <Trans>Voulez-vous accepter cette demande ?</Trans>
          </p>
        </section>

        <section>
          <Alert variant="info">
            <InfoCircle />
            <p>
              <Trans
                defaults="{{energyTotal}} MWh renouvelables seront ajoutés à l'énergie disponible de l'aménageur {{cpo}}."
                values={{
                  energyTotal: formatNumber(application.energy_total),
                  cpo: application.cpo.name,
                }}
              ></Trans>
            </p>
          </Alert>
        </section>
      </main>

      <footer>
        <Button
          icon={Check}
          label={
            forceValidation
              ? t("Verser, sans auditer, les certificats de fourniture")
              : t("Verser les certificats de fourniture")
          }
          variant="success"
          action={() => acceptApplication(forceValidation)}
          loading={acceptMeterReadingsApplication.loading}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>
    </Dialog>
  )
}

export default MeterReadingsApplicationAcceptDialog
