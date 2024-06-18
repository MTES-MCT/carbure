import useEntity from "carbure/hooks/entity"
import { Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import ApplicationStatus from "elec/components/application-status"
import { ElecAuditApplicationStatus } from "elec/types"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import MeterReadingsApplicationAcceptDialog from "./accept-dialog"
import MeterReadingsApplicationDetailsInProgress from "./details-in-progress"
import { MeterReadingsApplicationDetailsPending } from "./details-pending"
import MeterReadingsApplicationRejectDialog from "./reject-dialog"
import MeterReadingsApplicationHistory from "./details-history-copy"

export const MeterReadingsApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("application/:id")

  const meterReadingsApplicationResponse = useQuery(api.getMeterReadingsApplicationDetails, {
    key: "audit-meter-readings-application-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  const meterReadingsApplication = meterReadingsApplicationResponse.result?.data.data


  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }


  const acceptApplication = (force: boolean = false) => {
    if (!meterReadingsApplication) return
    portal((close) => (
      <MeterReadingsApplicationAcceptDialog
        application={meterReadingsApplication}
        onClose={close}
        forceValidation={force}
        onValidated={closeDialog}
      />
    ))
  }

  const rejectApplication = (force: boolean = false) => {
    if (!meterReadingsApplication) return
    portal((close) => (
      <MeterReadingsApplicationRejectDialog
        application={meterReadingsApplication}
        onClose={close}
        forceRejection={force}
        onRejected={closeDialog}
      />
    ))
  }

  const downloadSample = async () => {
    if (!meterReadingsApplication) return
    return api.downloadMeterReadingsApplication(entity.id, meterReadingsApplication.id)

  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} >
        <header>
          <ApplicationStatus status={meterReadingsApplication?.status} big />
          <h1>{t("Relevés T{{quarter}} {{year}} - {{cpo}}", {
            quarter: meterReadingsApplication?.quarter,
            year: meterReadingsApplication?.year,
            cpo: meterReadingsApplication?.cpo.name
          })}</h1>

        </header>

        {meterReadingsApplication?.status === ElecAuditApplicationStatus.Pending && (
          <MeterReadingsApplicationDetailsPending
            meterReadingsApplication={meterReadingsApplication}
            onAccept={acceptApplication}
            onReject={rejectApplication}
            onDownloadSample={downloadSample}
          />
        )}

        {meterReadingsApplication?.status === ElecAuditApplicationStatus.AuditInProgress && (
          <MeterReadingsApplicationDetailsInProgress
            meterReadingsApplication={meterReadingsApplication}
            onAccept={acceptApplication}
            onReject={rejectApplication}
            onDownloadSample={downloadSample}
          />
        )}

        {meterReadingsApplication?.status && [ElecAuditApplicationStatus.Accepted, ElecAuditApplicationStatus.Rejected].includes(meterReadingsApplication.status) && (
          <MeterReadingsApplicationHistory
            meterReadingsApplication={meterReadingsApplication}
          />
        )
        }

        {meterReadingsApplicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal >
  )
}

export default MeterReadingsApplicationDetailsDialog
