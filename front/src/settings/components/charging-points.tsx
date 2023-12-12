import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Download, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { Grid, LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatDate, formatNumber } from "common/utils/formatters"
import * as apiAdmin from "elec-admin/api"
import ChargingPointsApplicationDetailsDialog from "elec-admin/components/charging-points/application-details-dialog"
import ApplicationStatus from "elec/components/charging-points/application-status"
import ElecChargingPointsFileUpload from "elec/components/charging-points/upload-dialog"
import { ElecChargingPointsSnapshot, ElecChargingPointsApplication, ElecChargingPointsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import * as apiCpo from "../api/elec"
import { elecChargingPointsApplications } from "elec/__test__/data"
import Metric from "common/components/metric"
import { useMatch } from "react-router-dom"

const ElecSettings = ({ companyId }: { companyId: number }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isCPO } = entity
  const matchStatus = useMatch("/org/:entity/:view/*")


  const api = matchStatus?.params.view === "entities" ? apiAdmin : apiCpo
  const portal = usePortal()

  const applicationsResponse = useQuery(api.getChargingPointsApplications, {
    key: "charging-points-applications",
    params: [entity.id, companyId],
  })

  const applications = applicationsResponse.result?.data.data ?? []
  // const applications = elecChargingPointsApplications // TEST with applications

  const acceptedApplications = applications.filter(app => app.status === ElecChargingPointsApplicationStatus.Accepted)

  const applicationsSnapshot: ElecChargingPointsSnapshot = {
    station_count: acceptedApplications.reduce((acc, app) => acc + app.station_count, 0),
    charging_point_count: acceptedApplications.reduce((acc, app) => acc + app.charging_point_count, 0),
    power_total: acceptedApplications.reduce((acc, app) => acc + app.power_total, 0),
  }
  const isEmpty = applications.length === 0


  function showUploadDialog() {
    const pendingApplicationAlreadyExists = applications.filter(app => app.status === ElecChargingPointsApplicationStatus.Pending).length > 0
    portal((resolve) => (
      <ElecChargingPointsFileUpload onClose={resolve} pendingApplicationAlreadyExists={pendingApplicationAlreadyExists} />
    ))
  }

  function showApplicationDetails(application: ElecChargingPointsApplication) {
    portal((resolve) => (
      <ChargingPointsApplicationDetailsDialog onClose={resolve} application={application} companyId={companyId} />
    ))
  }

  function downloadChargingPoints() {
    api.downloadChargingPoints(entity.id, companyId)
  }

  return (
    <Panel id="elec-charging-points">
      <header>
        <h1>
          {t("Inscriptions de points de recharge")}
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
        {applicationsSnapshot.charging_point_count > 0 &&
          <Button

            variant="secondary"
            icon={Download}
            action={downloadChargingPoints}
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
        <>

          <section>
            <Grid style={{ gridGap: 24 }}>
              <Metric value={formatNumber(Math.round(applicationsSnapshot.power_total))} label={t("Kw cumulés")} />
              <Metric value={applicationsSnapshot.station_count} label={t("Stations")} />
              <Metric value={applicationsSnapshot.charging_point_count} label={t("Points de recharge")} />
            </Grid>
          </section>
          <Table
            rows={applications}
            onAction={showApplicationDetails}
            columns={[
              {
                header: t("Statut"),
                cell: (application) => <ApplicationStatus status={application.status} />,
              },
              {
                header: t("Date"),
                cell: (application) => (
                  <Cell
                    text={`${formatDate(application.application_date)}`}
                  />
                ),
              },
              {
                header: t("Puissance cumulée"),
                cell: (application) => (
                  <Cell
                    text={`${formatNumber(Math.round(application.power_total))}` + " kW"}
                  />
                ),
              },
              {
                header: t("Stations"),
                cell: (application) => (
                  <Cell
                    text={`${formatNumber(application.station_count)}`}
                  />
                ),
              },
              {
                header: t("Points de recharge"),
                cell: (application) => (
                  <Cell
                    text={`${formatNumber(application.charging_point_count)}`}
                  />
                ),
              },

            ]}
          />
        </>


      )}

      {applicationsResponse.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default ElecSettings