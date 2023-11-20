import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Check, Cross, Download, Plus, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import Tag from "common/components/tag"
import { useMutation } from "common/hooks/async"
import { download } from "common/services/api"
import { formatDate } from "common/utils/formatters"
import SubscriptionStatus from "elec/components/charging-points/subscription-status"
import { ElecChargingPointsSubscription, ElecChargingPointsSubscriptionCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { subscribeChargingPoints } from "settings/api/elec"
import * as api from "elec-admin/api"
export type SubscriptionDialogProps = {
  subscription: ElecChargingPointsSubscription
  onClose: () => void

}

export const SubscriptionDialog = ({
  subscription,
  onClose,
}: SubscriptionDialogProps) => {
  const { t } = useTranslation()

  const downloadChargingPoints = () => {
    // api.downloadSubscriptionChargingPoints(subscription.id)
  }

  const rejectSubscription = () => {

  }

  const acceptSubscription = () => {

  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <SubscriptionStatus status={subscription.status} big />

        <h1>{t("Inscription des points de recharge")}</h1>
      </header>

      <main>

        <section>
          <p style={{ textAlign: 'left' }}>
            <Trans
              values={{
                applicationDate: formatDate(subscription.application_date),
              }}
              count={subscription.charging_point_count}
              defaults="La demande d'inscription a été faite pour <b>{{count}} points de recharge</b> le <b>{{applicationDate}}</b>." />
          </p>

          <p>
            <Button icon={Download} label={t("Exporter les points de charge")} variant="secondary" action={downloadChargingPoints} />
          </p>
        </section>
      </main>

      <footer>

        <Button icon={Check} label={t("Valider l'inscription")} variant="success" action={acceptSubscription} />
        <Button icon={Cross} label={t("Refuser")} variant="danger" action={rejectSubscription} />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default SubscriptionDialog


