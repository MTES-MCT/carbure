import { useNotify, useNotifyError } from "common/components/notifications";
import { useMutation } from "common/hooks/async";
import { ElecMeterReadingsApplicationDetails } from "elec/types";
import 'leaflet-defaulticon-compatibility';
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css'; // Re-uses images from ~leaflet package
import 'leaflet/dist/leaflet.css';
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";
import * as api from "../../api";
import ApplicationSampleGeneration from "../sample/application-generation";
import ApplicationSummary from "./details-application-summary";

export type GenerationState = "generation" | "verification" | "email" | "confirmation"

interface MeterReadingsApplicationDetailsPendingProps {
  meterReadingsApplication: ElecMeterReadingsApplicationDetails | undefined
  onAccept: (force: boolean) => void
  onReject: (force: boolean) => void
  onDownloadSample: () => void
}
export const MeterReadingsApplicationDetailsPending = ({
  meterReadingsApplication,
  onAccept,
  onReject,
  onDownloadSample
}: MeterReadingsApplicationDetailsPendingProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const navigate = useNavigate()
  const location = useLocation()


  const startMeterReadingsApplicationAuditMutation = useMutation(api.startMeterReadingsApplicationAudit, {
    invalidates: ["audit-meter-readings-application-details", "audit-meter-readings-applications"]
  })

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const startAudit = async (entityId: number, applicationId: number, chargePointIds: string[]) => {
    startMeterReadingsApplicationAuditMutation.execute(entityId, applicationId)
      .then(() => {
        notify(t("L'audit des relevés des {{count}} points de recharge a bien été initié.", { count: chargePointIds.length }), { variant: "success" })
        closeDialog()
      })
      .catch((err) => {
        notifyError(err, t("Impossible d'initier l'audit des relevés des points de recharge."))
      })
  }


  return (
    <>
      <ApplicationSampleGeneration
        application={meterReadingsApplication}
        onAccept={onAccept}
        onReject={onReject}
        onDownloadSample={onDownloadSample}
        onStartAudit={startAudit}
        summary={<ApplicationSummary application={meterReadingsApplication} />}
        startAuditQueryLoading={startMeterReadingsApplicationAuditMutation.loading}
        generateSampleQuery={api.generateMeterReadingsAuditSample}
        emailIntro={`Bonjour%20${meterReadingsApplication?.cpo.name}%0D%0A%0D%0A%0D%0AAfin%20de%20valider%20votre%20relevé%20de%20points%20de%20recharge%2C%20un%20audit%20doit%20%C3%AAtre%20men%C3%A9%20sur%20les%20points%20de%20recharge%20s%C3%A9lectionn%C3%A9s%20ci-joints.%0D%0A%0D%0A%0D%0AL'inspecteur%20doit%20remplir%20le%20tableau%20en%20respectant%20le%20format%20suivant%20%3A%0D%0A%0D%0A%0D%0A`}
      />
    </>
  )
}
