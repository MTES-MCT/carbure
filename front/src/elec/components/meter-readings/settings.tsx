import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Check, Cross, Download, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell, actionColumn } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatNumber } from "common/utils/formatters"
import * as apiAdmin from "elec-admin/api"
import * as apiCpo from "elec/api-cpo"
import { ElecMeterReadingsApplication, ElecAuditApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"

import { compact } from "common/utils/collection"
import { useMatch } from "react-router-dom"
import ElecMeterReadingsFileUpload from "./upload-dialog"
import ApplicationStatus from "../application-status"
import MeterReadingsApplicationAcceptDialog from "elec-audit-admin/components/meter-readings/accept-dialog"
import MeterReadingsApplicationRejectDialog from "elec-audit-admin/components/meter-readings/reject-dialog"
import MeterReadingsApplicationsTable from "./table"

const ElecMeterReadingsSettings = ({ companyId }: { companyId: number }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isCPO } = entity
  const matchStatus = useMatch("/org/:entity/:view/*")


  const api = matchStatus?.params.view === "entities" ? apiAdmin : apiCpo
  const portal = usePortal()

  const applicationsResponse = useQuery(api.getMeterReadingsApplications, {
    key: "meter-readings-applications",
    params: [entity.id, companyId],
  })

  const applications = applicationsResponse.result?.data.data ?? []
  // const applications = elecMeterReadingsApplications // TEST with applications
  const isEmpty = applications.length === 0

  function showUploadDialog() {

    const pendingApplicationAlreadyExists = applications.filter(app => app.status === ElecAuditApplicationStatus.Pending).length > 0
    portal((resolve) => (
      <ElecMeterReadingsFileUpload onClose={resolve} pendingApplicationAlreadyExists={pendingApplicationAlreadyExists} companyId={companyId} />
    ))
  }



  const downloadMeterReadingsApplication = (application: ElecMeterReadingsApplication) => {
    return api.downloadMeterReadingsApplicationDetails(entity.id, companyId, application.id)
  }

  return (
    <Panel id="elec-meter-readings">
      <header>
        <h1>
          {t("Relevés trimestriels")}
        </h1>

        {isCPO && (
          <Button
            asideX={true}
            variant="primary"
            icon={Plus}
            action={showUploadDialog}
            label={t("Transmettre mes relevés trimestriels")}
          />
        )}
        {/* {applicationsSnapshot.charge_point_count > 0 &&
          <Button
            asideX={!isCPO}
            variant="secondary"
            icon={Download}
            action={downloadChargePoints}
            label={t("Exporter les points de recharge")}
          />
        } */}
      </header>



      {isEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun relevé trimestriel trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isEmpty && (
        <>
          <MeterReadingsApplicationsTable
            applications={applications}
            onDownloadMeterReadingsApplication={downloadMeterReadingsApplication}
          />
        </>


      )}

      {applicationsResponse.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default ElecMeterReadingsSettings
