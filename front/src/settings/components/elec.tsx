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
import ChargingPointsApplicationDetailsDialog from "elec-admin/components/charging-points/application-details-dialog"
import ApplicationStatus from "elec/components/charging-points/application-status"
import ElecChargingPointsFileUpload from "elec/components/charging-points/upload-dialog"
import { ElecChargingPointsSnapshot, ElecChargingPointsApplication } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import * as apiCpo from "../api/elec"
import { elecChargingPointsApplications } from "elec/__test__/data"

const ElecSettings = ({ companyId }: { companyId: number }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isCPO, isAdmin } = entity

  const api = isAdmin ? apiAdmin : apiCpo
  const portal = usePortal()

  const applicationsResponse = useQuery(api.getChargingPointsApplications, {
    key: "charging-points-applications",
    params: [entity.id, companyId],
  })

  const applications = applicationsResponse.result?.data.data ?? []
  // const applications = elecChargingPointsApplications // TEST with applications

  const applicationsSnapshot: ElecChargingPointsSnapshot = {
    station_count: applications.reduce((acc, app) => acc + app.station_count, 0),
    charging_point_count: applications.reduce((acc, app) => acc + app.charging_point_count, 0),
    power_total: applications.reduce((acc, app) => acc + app.power_total, 0),
  }
  const isEmpty = applications.length === 0


  function showUploadDialog() {
    portal((resolve) => (
      <ElecChargingPointsFileUpload onClose={resolve} />
    ))
  }

  function showApplicationDetails(application: ElecChargingPointsApplication) {
    portal((resolve) => (
      <ChargingPointsApplicationDetailsDialog onClose={resolve} application={application} companyId={companyId} />
    ))
  }

  function downloadChargingPointsApplications() {
    api.downloadChargingPointsApplications(entity.id, companyId)
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
        {applicationsSnapshot.charging_point_count > 0 &&
          <Button
            asideX
            variant="secondary"
            icon={Plus}
            action={downloadChargingPointsApplications}
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