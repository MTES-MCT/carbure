import useEntity, { useRights } from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatDate, formatNumber } from "common/utils/formatters"
import SubscriptionStatus from "elec/components/charging-points/subscription-status"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/elec"
import { ElecChargingPointsSubscription, ElecChargingPointsSnapshot } from "elec/types"
import ElecChargingPointsFileUpload from "elec/components/charging-points/upload"
import { elecChargingPointsSubscriptions } from "elec/__test__/data"

const ElecSettings = () => {
  const { t } = useTranslation()
  const rights = useRights()
  const entity = useEntity()
  const portal = usePortal()

  const subscriptionsResponse = useQuery(api.getChargingPointsSubscriptions, {
    key: "charging-points-subscriptions",
    params: [entity.id],
  })

  const subscriptions = subscriptionsResponse.result?.data.data ?? []

  // const subscriptions = elecChargingPointsSubscriptions // TEST with subscriptions





  const subscriptionsSnapshot: ElecChargingPointsSnapshot = {
    station_count: subscriptions.reduce((acc, app) => acc + app.station_count, 0),
    charging_point_count: subscriptions.reduce((acc, app) => acc + app.charging_point_count, 0),
    power_total: subscriptions.reduce((acc, app) => acc + app.power_total, 0),
  }
  const isEmpty = subscriptions.length === 0


  function showUploadDialog() {
    portal((resolve) => (
      <ElecChargingPointsFileUpload onClose={resolve} />
    ))
  }

  return (
    <Panel id="elec-charging-points">
      <header>
        <h1>
          <Trans>Inscriptions de points de recharge</Trans>
        </h1>
        <Button
          asideX
          variant="primary"
          icon={Plus}
          action={showUploadDialog}
          label={t("Inscrire des points de recharge")}
        />
      </header>

      {isEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun point de recharge trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isEmpty && (
        <Table
          rows={subscriptions}
          columns={[
            {
              header: t("Statut"),
              cell: (subscription) => <SubscriptionStatus status={subscription.status} />,
            },
            {
              header: t("Date"),
              cell: (subscription) => (
                <Cell
                  text={`${formatDate(subscription.date)}`}
                />
              ),
            },
            {
              header: subscriptionsSnapshot.power_total + " kW " + t("cumulé"),
              cell: (subscription) => (
                <Cell
                  text={`${formatNumber(subscription.power_total)}` + " kW"}
                />
              ),
            },
            {
              header: subscriptionsSnapshot.station_count + " " + t("Stations"),
              cell: (subscription) => (
                <Cell
                  text={`${formatNumber(subscription.station_count)}`}
                />
              ),
            },
            {
              header: subscriptionsSnapshot.charging_point_count + " " + t("Points de recharge"),
              cell: (subscription) => (
                <Cell
                  text={`${formatNumber(subscription.charging_point_count)}`}
                />
              ),
            },

          ]}
        />
      )}

      {subscriptionsResponse.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default ElecSettings