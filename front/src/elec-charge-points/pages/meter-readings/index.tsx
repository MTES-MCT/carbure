import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import * as api from "elec/api-cpo"
import MeterReadingsApplicationsTable from "elec/components/meter-readings/table"
import {
  ElecAuditApplicationStatus,
  ElecMeterReadingsApplication,
  MeterReadingsApplicationUrgencyStatus,
} from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { useElecMeterReadingsSettings } from "./index.hooks"
import ElecMeterReadingsFileUpload from "./upload-dialog"
import { useMutation } from "common/hooks/async"
import { deleteChargePointsApplication } from "./api"

type ElecMeterReadingsSettingsProps = {
  companyId: number
  contentOnly?: boolean
}
const ElecMeterReadingsSettings = ({
  companyId,
  contentOnly = false,
}: ElecMeterReadingsSettingsProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const portal = usePortal()

  const {
    applications,
    applicationsQuery,
    chargePointCount,
    currentApplication,
    quarterString,
    urgencyStatus,
    currentApplicationPeriod,
    isApplicationsEmpty,
  } = useElecMeterReadingsSettings({ entityId: entity.id, companyId })

  const deleteApplication = useMutation(
    (id: number) => deleteChargePointsApplication(entity.id, id),
    { invalidates: ["meter-readings-applications"] }
  )

  function showUploadDialog() {
    const hasPendingApplications = applications.some(
      (app) => app.status === ElecAuditApplicationStatus.Pending
    )

    const hasAcceptedApplicationForCurrentQuarter = applications.some(
      (app) =>
        app.quarter === currentApplicationPeriod?.quarter &&
        app.year === currentApplicationPeriod.year &&
        app.status === ElecAuditApplicationStatus.Accepted
    )

    portal((resolve) => (
      <ElecMeterReadingsFileUpload
        onClose={resolve}
        companyId={companyId}
        currentApplicationPeriod={currentApplicationPeriod!}
        hasPendingApplications={hasPendingApplications}
        hasAcceptedApplicationForCurrentQuarter={
          hasAcceptedApplicationForCurrentQuarter
        }
      />
    ))
  }

  const downloadMeterReadingsApplication = (
    application: ElecMeterReadingsApplication
  ) => {
    return api.downloadMeterReadingsApplicationDetails(
      entity.id,
      companyId,
      application.id
    )
  }

  return (
    <section>
      {!contentOnly && <h1>{t("Relevés trimestriels")}</h1>}

      {chargePointCount === 0 && (
        <p>
          <Trans>Vous n'avez aucun relevé à déclarer</Trans>
        </p>
      )}
      {!!chargePointCount && chargePointCount > 1 && (
        <Button
          asideX={true}
          variant={
            currentApplication
              ? "primary"
              : urgencyStatus === MeterReadingsApplicationUrgencyStatus.High
                ? "warning"
                : urgencyStatus ===
                    MeterReadingsApplicationUrgencyStatus.Critical
                  ? "danger"
                  : "primary"
          }
          icon={Plus}
          action={showUploadDialog}
          label={t("Transmettre mes relevés trimestriels {{quarter}}", {
            quarter: quarterString,
          })}
        />
      )}

      {isApplicationsEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun relevé trimestriel trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isApplicationsEmpty && (
        <>
          <MeterReadingsApplicationsTable
            applications={applications}
            onDownloadMeterReadingsApplication={
              downloadMeterReadingsApplication
            }
            onDeleteMeterReadingsApplication={deleteApplication.execute}
          />
        </>
      )}

      {applicationsQuery.loading && <LoaderOverlay />}
    </section>
  )
}

export default ElecMeterReadingsSettings
