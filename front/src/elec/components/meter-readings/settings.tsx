import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import * as api from "elec/api-cpo"
import { ElecAuditApplicationStatus, ElecMeterReadingsApplication, MeterReadingsApplicationUrgencyStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import MeterReadingsApplicationsTable from "./table"
import ElecMeterReadingsFileUpload from "./upload-dialog"
import { elecMeterReadingsApplicationsResponseMissing, elecMeterReadingsApplicationsResponsePending } from "elec/__test__/data"


const ElecMeterReadingsSettings = ({ companyId }: { companyId: number }) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const portal = usePortal()

  const applicationsQuery = useQuery(api.getMeterReadingsApplications, {
    key: "meter-readings-applications",
    params: [entity.id, companyId],
  })

  // const applicationsResponse = applicationsQuery.result?.data.data
  // const applicationsResponse = elecMeterReadingsApplicationsResponseMissing
  const applicationsResponse = elecMeterReadingsApplicationsResponsePending
  const applications = applicationsResponse?.applications ?? [] // TEST with applications
  const currentApplicationPeriod = applicationsResponse?.current_application_period
  const currentApplication = applicationsResponse?.current_application
  console.log('applications:', applications)

  const isEmpty = applications.length === 0

  const urgencyStatus = currentApplicationPeriod?.urgency_status
  const quarterString = t("T{{quarter}} {{year}}", { quarter: currentApplicationPeriod?.quarter, year: currentApplicationPeriod?.year })


  function showUploadDialog() {
    const pendingApplicationAlreadyExists = currentApplication?.status === ElecAuditApplicationStatus.Pending
    if (currentApplication && currentApplication.status !== ElecAuditApplicationStatus.Pending) return
    portal((resolve) => (
      <ElecMeterReadingsFileUpload
        onClose={resolve}
        pendingApplicationAlreadyExists={pendingApplicationAlreadyExists}
        companyId={companyId}
        currentApplicationPeriod={currentApplicationPeriod!}
      />
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


        <Button
          asideX={true}
          variant={currentApplication ? "primary" : urgencyStatus === MeterReadingsApplicationUrgencyStatus.High ? "warning" : urgencyStatus === MeterReadingsApplicationUrgencyStatus.Critical ? "danger" : "primary"}
          icon={Plus}
          disabled={currentApplication && currentApplication.status !== ElecAuditApplicationStatus.Pending}
          action={showUploadDialog}
          label={t("Transmettre mes relevés trimestriels {{quarter}}", { quarter: quarterString })}
        />

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

      {applicationsQuery.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default ElecMeterReadingsSettings
