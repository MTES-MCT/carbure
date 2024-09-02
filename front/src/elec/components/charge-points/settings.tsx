import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Download, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { Grid, LoaderOverlay, Panel } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { formatNumber } from "common/utils/formatters"
import * as apiAdmin from "elec-admin/api"
import ElecChargePointsFileUpload from "elec/components/charge-points/upload-dialog"
import {
  ElecChargePointsApplication,
  ElecAuditApplicationStatus,
  ElecChargePointsSnapshot,
} from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import * as apiCpo from "elec/api-cpo"
import Metric from "common/components/metric"

import { useMatch } from "react-router-dom"
import ChargePointsApplicationsTable from "./table"

const ElecChargePointsSettings = ({ companyId }: { companyId: number }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isCPO } = entity
  const matchStatus = useMatch("/org/:entity/:view/*")

  const api = matchStatus?.params.view === "entities" ? apiAdmin : apiCpo
  const portal = usePortal()

  const applicationsResponse = useQuery(api.getChargePointsApplications, {
    key: "charge-points-applications",
    params: [entity.id, companyId],
  })

  const applications = applicationsResponse.result?.data.data ?? []

  const acceptedApplications = applications.filter(
    (app) => app.status === ElecAuditApplicationStatus.Accepted
  )

  const applicationsSnapshot: ElecChargePointsSnapshot = {
    station_count: acceptedApplications.reduce(
      (acc, app) => acc + app.station_count,
      0
    ),
    charge_point_count: acceptedApplications.reduce(
      (acc, app) => acc + app.charge_point_count,
      0
    ),
    power_total: acceptedApplications.reduce(
      (acc, app) => acc + app.power_total,
      0
    ),
  }
  const isEmpty = applications.length === 0

  function showUploadDialog() {
    portal((resolve) => <ElecChargePointsFileUpload onClose={resolve} />)
  }

  function downloadChargePoints() {
    api.downloadChargePoints(entity.id, companyId)
  }

  const downloadChargePointsApplication = (
    application: ElecChargePointsApplication
  ) => {
    return api.downloadChargePointsApplicationDetails(
      entity.id,
      companyId,
      application.id
    )
  }

  return (
    <Panel id="elec-charge-points">
      <header>
        <h1>{t("Inscriptions de points de recharge")}</h1>

        {isCPO && (
          <Button
            asideX={true}
            variant="primary"
            icon={Plus}
            action={showUploadDialog}
            label={t("Inscrire des points de recharge")}
          />
        )}
        {applicationsSnapshot.charge_point_count > 0 && (
          <Button
            asideX={!isCPO}
            variant="secondary"
            icon={Download}
            action={downloadChargePoints}
            label={t("Exporter les points de recharge")}
          />
        )}
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
              <Metric
                value={formatNumber(
                  Math.round(applicationsSnapshot.power_total)
                )}
                label={t("Kw cumulés")}
              />
              <Metric
                value={applicationsSnapshot.station_count}
                label={t("Stations")}
              />
              <Metric
                value={applicationsSnapshot.charge_point_count}
                label={t("Points de recharge")}
              />
            </Grid>
          </section>
          <ChargePointsApplicationsTable
            applications={applications}
            onDownloadChargePointsApplication={downloadChargePointsApplication}
          />
        </>
      )}

      {applicationsResponse.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default ElecChargePointsSettings
