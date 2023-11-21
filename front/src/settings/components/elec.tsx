import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatDate, formatNumber } from "common/utils/formatters"
import * as apiAdmin from "elec-admin/api"
import ChargingPointsSubscriptionDetailsDialog from "elec-admin/components/charging-points/subscription-details-dialog"
import SubscriptionStatus from "elec/components/charging-points/subscription-status"
import ElecChargingPointsFileUpload from "elec/components/charging-points/upload-dialog"
import { ElecChargingPointsSnapshot, ElecChargingPointsSubscription } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import * as apiCpo from "../api/elec"
import { elecChargingPointsSubscriptions } from "elec/__test__/data"

const ElecSettings = ({ companyId }: { companyId: number }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isCPO, isAdmin } = entity

  const api = isAdmin ? apiAdmin : apiCpo
  const portal = usePortal()

  const subscriptionsResponse = useQuery(api.getChargingPointsSubscriptions, {
    key: "charging-points-subscriptions",
    params: [entity.id, companyId],
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

  function showSubscriptionDetails(subscription: ElecChargingPointsSubscription) {
    portal((resolve) => (
      <ChargingPointsSubscriptionDetailsDialog onClose={resolve} subscription={subscription} companyId={companyId} />
    ))
  }

  function downloadChargingPointsSubscriptions() {
    api.downloadChargingPointsSubscriptions(entity.id, companyId)
  }

  return (
    <Panel id="elec-charging-points">
      <header>
        <h1>
          <Trans>Inscriptions de points de recharge</Trans>
        </h1>

        {isCPO && (
          <Button
            asideX
            variant="primary"
            icon={Plus}
            action={showUploadDialog}
            label={t("Inscrire des points de recharge")}
          />
        )}
        {subscriptionsSnapshot.charging_point_count > 0 &&
          <Button
            asideX
            variant="secondary"
            icon={Plus}
            action={downloadChargingPointsSubscriptions}
            label={t("Exporter les points de recharge")}
          />
        }
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
          onAction={showSubscriptionDetails}
          columns={[
            {
              header: t("Statut"),
              cell: (subscription) => <SubscriptionStatus status={subscription.status} />,
            },
            {
              header: t("Date"),
              cell: (subscription) => (
                <Cell
                  text={`${formatDate(subscription.application_date)}`}
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