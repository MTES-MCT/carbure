import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Check, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import ApplicationStatus from "elec/components/application-status"
import { ElecChargePointsApplicationDetails } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../../api"
export type ApplicationDialogProps = {
  application: ElecChargePointsApplicationDetails
  onClose: () => void
  onValidated: () => void
  forceValidation: boolean
}

export const ChargePointsApplicationAcceptDialog = ({
  application,
  onClose,
  onValidated,
  forceValidation,
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const acceptChargePointsApplication = useMutation(
    api.acceptChargePointsApplication,
    {
      invalidates: [
        "audit-charge-points-applications",
        "elec-admin-audit-snapshot",
        `nav-stats-${entity.id}`,
      ],
      onSuccess() {
        onClose()
        onValidated()
        notify(
          t(
            "L'inscription des {{count}} points de recharge ont été acceptés !",
            {
              count: application.charge_point_count,
            }
          ),
          { variant: "success" }
        )
      },
      onError(err) {
        notifyError(
          err,
          t("Impossible d'accepter l'inscription des points de recharge")
        )
      },
    }
  )

  const acceptApplication = (forceValidation: boolean) => {
    acceptChargePointsApplication.execute(
      entity.id,
      application.id,
      forceValidation
    )
  }

  const sample = application.sample
  return (
    <Dialog onClose={onClose}>
      <header>
        <ApplicationStatus status={application.status} big />

        <h1>{t("Accepter les points de recharge")}</h1>
      </header>

      <main>
        <section>
          <p style={{ textAlign: "left" }}>
            <Trans
              values={{
                applicationDate: formatDate(application.application_date),
              }}
              count={application.charge_point_count}
              defaults="Valider l'inscription de <b>{{count}} points de recharge</b> importés le <b>{{applicationDate}}</b> ?"
            />
          </p>
          {sample && (
            <Alert icon={AlertCircle} variant="info" multiline>
              <Trans
                defaults={
                  "L'aménageur <b>{{cpo}}</b> sera notifié et pourra visualiser les points de recharge depuis son espace Carbure."
                }
                values={{ cpo: application.cpo.name }}
              />
            </Alert>
          )}
        </section>
      </main>

      <footer>
        <Button
          icon={Check}
          label={
            forceValidation
              ? t("Accepter l'inscription sans audit")
              : t("Accepter l'inscription")
          }
          variant="success"
          action={() => acceptApplication(forceValidation)}
          loading={acceptChargePointsApplication.loading}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>
    </Dialog>
  )
}

export default ChargePointsApplicationAcceptDialog
