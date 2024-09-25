import useEntity from "carbure/hooks/entity"
import { Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import * as api from "elec-auditor/api"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import ApplicationStatus from "./application-status"
import { ElecAuditorApplicationsStatus } from "elec-auditor/types"
import ApplicationDetailsPending from "./details-pending"

export const ApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("application/:id")

  const applicationResponse = useQuery(api.getApplicationDetails, {
    key: "elec-auditor-application-details",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })
  const application = applicationResponse.result?.data.data

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const downloadSample = async () => {
    return api.downloadSample(entity.id, application!.id)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <ApplicationStatus status={application?.status} big />
          <h1>{t("Audit de points de recharge")}</h1>
        </header>

        {application?.status ===
          ElecAuditorApplicationsStatus.AuditInProgress && (
          <ApplicationDetailsPending
            application={application}
            onDownloadSample={downloadSample}
            onReportAccepted={closeDialog}
          />
        )}

        {application?.status === ElecAuditorApplicationsStatus.AuditDone && (
          <p>Done</p>
          // <ApplicationDetailsPending
          //   application={application}
          //   onDownloadSample={downloadSample}
          // />
        )}

        {applicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default ApplicationDetailsDialog
