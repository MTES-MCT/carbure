import useEntity, { useRights } from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatDate, formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/charging-points/application-status"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/elec"
import { ElecChargingPointsApplication, ElecChargingPointsSnapshot } from "elec/types"
import ElecChargingPointsFileUpload from "elec/components/charging-points/upload"

const ElecSettings = () => {
  const { t } = useTranslation()
  const rights = useRights()
  const entity = useEntity()
  const portal = usePortal()

  const applicationsResponse = useQuery(api.getChargingPointsApplications, {
    key: "elec-charging-points",
    params: [entity.id],
  })

  const applications = applicationsResponse.result ?? []
  const applicationsSnapshot: ElecChargingPointsSnapshot = {
    station_count: applications.reduce((acc, app) => acc + app.station_count, 0),
    charging_point_count: applications.reduce((acc, app) => acc + app.charging_point_count, 0),
    power_total: applications.reduce((acc, app) => acc + app.power_total, 0),
  }
  console.log('applications:', applications)
  const isEmpty = applications.length === 0

  function showApplicationDialog(application: ElecChargingPointsApplication) {
    // portal((resolve) => (
    //   <DoubleCountingApplicationDialog
    //     entity={entity}
    //     applicationID={dc.id}
    //     onClose={resolve}
    //   />
    // ))
  }

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
          rows={applications}
          onAction={showApplicationDialog}
          columns={[
            {
              header: t("Statut"),
              cell: (application) => <ApplicationStatus status={application.status} />,
            },
            {
              header: t("Date"),
              cell: (application) => (
                <Cell
                  text={`${formatDate(application.date)}`}
                />
              ),
            },
            {
              header: applicationsSnapshot.power_total + " kW " + t("cumulé"),
              cell: (application) => (
                <Cell
                  text={`${formatNumber(application.power_total)}` + " kW"}
                />
              ),
            },
            {
              header: applicationsSnapshot.station_count + " " + t("Stations"),
              cell: (application) => (
                <Cell
                  text={`${formatNumber(application.station_count)}`}
                />
              ),
            },
            {
              header: applicationsSnapshot.charging_point_count + " " + t("Points de recharge"),
              cell: (application) => (
                <Cell
                  text={`${formatNumber(application.charging_point_count)}`}
                />
              ),
            },

          ]}
        />
      )}

      {applicationsResponse.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default ElecSettings