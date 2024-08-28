import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import * as api from "elec/api-cpo"
import {
  ElecAuditApplicationStatus,
  ElecMeterReadingsApplication,
  MeterReadingsApplicationUrgencyStatus,
} from "elec/types"
import { Fragment, PropsWithChildren, useMemo } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useElecMeterReadingsSettings } from "./settings.hooks"
import MeterReadingsApplicationsTable from "./table"
import ElecMeterReadingsFileUpload from "./upload-dialog"

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

  function showUploadDialog() {
    portal((resolve) => (
      <ElecMeterReadingsFileUpload
        onClose={resolve}
        companyId={companyId}
        currentApplicationPeriod={currentApplicationPeriod!}
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

  // This component is currently used across two pages with minor UI differences.
  // In the future, the UI should be unified across both pages to maintain consistency.
  const Wrapper = contentOnly ? Fragment : Panel
  const HeaderOrSection = contentOnly ? "section" : "header"

  return (
    <Wrapper id="elec-meter-readings">
      <HeaderOrSection>
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
            disabled={
              currentApplication &&
              currentApplication.status !== ElecAuditApplicationStatus.Pending
            }
            action={showUploadDialog}
            label={t("Transmettre mes relevés trimestriels {{quarter}}", {
              quarter: quarterString,
            })}
          />
        )}
      </HeaderOrSection>

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
          />
        </>
      )}

      {applicationsQuery.loading && <LoaderOverlay />}
    </Wrapper>
  )
}

export default ElecMeterReadingsSettings
