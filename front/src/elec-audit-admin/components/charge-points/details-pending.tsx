import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { ElecChargePointsApplicationDetails } from "elec/types"
import "leaflet-defaulticon-compatibility"
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css" // Re-uses images from ~leaflet package
import "leaflet/dist/leaflet.css"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import ApplicationSampleGeneration from "../sample/application-generation"
import ApplicationSummary from "./details-application-summary"
import useEntity from "common/hooks/entity"

export type GenerationState =
  | "generation"
  | "verification"
  | "email"
  | "confirmation"

interface ChargePointsApplicationDetailsPendingProps {
  chargePointApplication: ElecChargePointsApplicationDetails | undefined
  onAccept: (force: boolean) => void
  onReject: (force: boolean) => void
  onDownloadSample: () => void
}
export const ChargePointsApplicationDetailsPending = ({
  chargePointApplication,
  onAccept,
  onReject,
  onDownloadSample,
}: ChargePointsApplicationDetailsPendingProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()

  const startApplicationAuditMutation = useMutation(
    api.startChargePointsApplicationAudit,
    {
      invalidates: [
        "audit-charge-points-application-details",
        "audit-charge-points-applications",
        "elec-admin-audit-snapshot",
        `nav-stats-${entity.id}`,
      ],
    }
  )

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const startAudit = async (
    entityId: number,
    applicationId: number,
    chargePointIds: string[]
  ) => {
    startApplicationAuditMutation
      .execute(entityId, applicationId)
      .then(() => {
        notify(
          t(
            "L'audit de l'échantillon des {{count}} points de recharge a bien été initié.",
            { count: chargePointIds.length }
          ),
          { variant: "success" }
        )
        closeDialog()
      })
      .catch((err) => {
        notifyError(
          err,
          t(
            "Impossible d'initier l'audit de l'inscription des points de recharge"
          )
        )
      })
  }

  return (
    <>
      <ApplicationSampleGeneration
        application={chargePointApplication}
        onAccept={onAccept}
        onReject={onReject}
        onDownloadSample={onDownloadSample}
        onStartAudit={startAudit}
        summary={<ApplicationSummary application={chargePointApplication} />}
        startAuditQueryLoading={startApplicationAuditMutation.loading}
        generateSampleQuery={api.generateChargePointsAuditSample}
        emailIntro={`Bonjour%20${chargePointApplication?.cpo.name}%0D%0A%0D%0A%0D%0AAfin%20de%20valider%20votre%20inscription%20de%20points%20de%20recharge%2C%20un%20audit%20doit%20%C3%AAtre%20men%C3%A9%20sur%20les%20points%20de%20recharge%20s%C3%A9lectionn%C3%A9s%20ci-joints.%0D%0A%0D%0A%0D%0AL'inspecteur%20doit%20remplir%20le%20tableau%20en%20respectant%20le%20format%20suivant%20%3A%0D%0A%0D%0A%0D%0A`}
      />
    </>
  )
}
