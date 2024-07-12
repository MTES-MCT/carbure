import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Divider } from "common/components/divider"
import { useHashMatch } from "common/components/hash-route"
import { Download, Edit, Send } from "common/components/icons"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import ChargePointsSampleMap from "elec-audit-admin/components/sample/sample-map"
import * as api from "elec-auditor/api"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import ApplicationSummary from "./details-application-summary"
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
    params: [entity.id, parseInt(match?.params.id!)],
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
      <Dialog onClose={closeDialog} >
        <header>
          <ApplicationStatus status={application?.status} big />
          <h1>{t("Audit de points de recharge")}</h1>
        </header>

        {application?.status === ElecAuditorApplicationsStatus.AuditInProgress && (
          <ApplicationDetailsPending
            application={application}
            onDownloadSample={downloadSample}
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
    </Portal >
  )
}


interface MailtoButtonProps {
  cpoName?: string
  auditorName?: string
  chargePointCount?: number

}

const MailtoButton = ({ cpoName, auditorName, chargePointCount }: MailtoButtonProps) => {
  const { t } = useTranslation()
  const email = "valorisation-recharge@developpement-durable.gouv.fr"
  const subject = t(`[CarbuRe - Audit Elec] Rapport d'audit de {{cpoName}} par {{auditorName}}`, { cpoName, auditorName })
  const body = t(`Bonjour%2C%E2%80%A8%0D%0AVous%20trouverez%20ci-joint%20le%20rapport%20d%E2%80%99audit%20pour%20les%20{{chargePointCount}}%20points%20de%20recharge%20de%20l%E2%80%99am%C3%A9nageur%20{{cpoName}}%20que%20nous%20venons%20de%20r%C3%A9aliser.%0D%0A%0D%0AMerci%20beaucoup%E2%80%A8%0D%0ABien%20cordialement%2C`, { cpoName, chargePointCount })
  const mailto = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${body}`
  return <Button icon={Send} label={t("Envoyer le rapport d'audit")} variant="primary" href={mailto} disabled={!cpoName} />
}


export default ApplicationDetailsDialog
