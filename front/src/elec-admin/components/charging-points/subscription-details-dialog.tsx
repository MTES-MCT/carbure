import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Cross, Download, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "elec-admin/api"
import SubscriptionStatus from "elec/components/charging-points/subscription-status"
import { ElecChargingPointsSubscription, ElecChargingPointsSubscriptionStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
export type SubscriptionDialogProps = {
  subscription: ElecChargingPointsSubscription
  onClose: () => void
  companyId: number
}

export const ChargingPointsSubscriptionDetailsDialog = ({
  subscription,
  onClose,
  companyId,
}: SubscriptionDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const downloadChargingPoints = () => {
    return api.downloadChargingPointsSubscriptionDetails(entity.id, companyId, subscription.id)
  }

  const acceptChargingPointsSubscription = useMutation(api.acceptChargingPointsSubscription, {
    invalidates: ["charging-points-subscriptions"],
    onSuccess() {
      onClose()
      notify(t("Les {{count}} points de recharge ont été acceptés !", { count: subscription.charging_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible d'accepter les points de recharge"))
    },
  })

  const rejectChargingPointsSubscription = useMutation(api.rejectChargingPointsSubscription, {
    invalidates: ["charging-points-subscriptions"],
    onSuccess() {
      onClose()
      notify(t("La demande d'inscription pour les {{count}} points de recharge a été refusée !", { count: subscription.charging_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible de refuser les points de recharge"))
    },
  })

  const rejectSubscription = () => {
    rejectChargingPointsSubscription.execute(entity.id, companyId, subscription.id)
  }

  const acceptSubscription = () => {
    acceptChargingPointsSubscription.execute(entity.id, companyId, subscription.id)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <SubscriptionStatus status={subscription.status} big />

        <h1>{t("Inscription de points de recharge")}</h1>
      </header>

      <main>

        <section>
          <p style={{ textAlign: 'left' }}>
            <Trans
              values={{
                applicationDate: formatDate(subscription.application_date),
              }}
              count={subscription.charging_point_count}
              defaults="La demande d'inscription a été faite le <b>{{applicationDate}}</b> pour <b>{{count}} points de recharge</b>." />
          </p>

          <p>
            <Button icon={Download} label={t("Exporter les points de charge")} variant="secondary" action={downloadChargingPoints} />
          </p>
          {!entity.isAdmin && subscription.status === ElecChargingPointsSubscriptionStatus.Pending && (
            <p><i>
              {t("En attente de validation de la DGEC.")}
            </i></p>
          )}
        </section>
      </main>

      <footer>

        {entity.isAdmin && subscription.status === ElecChargingPointsSubscriptionStatus.Pending && (
          <>
            <Button icon={Check} label={t("Valider l'inscription")} variant="success" action={acceptSubscription} />
            <Button icon={Cross} label={t("Refuser")} variant="danger" action={rejectSubscription} />
          </>
        )}
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default ChargingPointsSubscriptionDetailsDialog


