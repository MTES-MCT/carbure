import { Stepper } from "@codegouvfr/react-dsfr/Stepper"
import useEntity from "carbure/hooks/entity"
import { EntityPreview } from "carbure/types"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { Check, ChevronLeft, Cross, Download, Send } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { ElecChargePointsApplicationSample } from "elec-audit-admin/types"
import { ElecAuditApplicationStatus, ElecChargePointsApplication, ElecChargePointsApplicationDetails } from "elec/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import ApplicationSummary from "./details-application-summary"
import SampleGenerationForm from "./details-sample-generation-form"
import SampleSummary from "./details-sample-summary"




interface ChargingPointsApplicationDetailsInProgressProps {
  chargePointApplication: ElecChargePointsApplicationDetails | undefined
  onAccept: (force?: boolean) => void
  onReject: (force?: boolean) => void
  onDownloadSample: () => void
}
export const ChargingPointsApplicationDetailsInProgress = ({
  chargePointApplication,
  onAccept,
  onReject,
  onDownloadSample
}: ChargingPointsApplicationDetailsInProgressProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const navigate = useNavigate()
  const location = useLocation()

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <>

      <main>

        <section>
          <ApplicationSummary application={chargePointApplication} />
        </section>
        <Divider />
        <section>

          <SampleSummary sample={chargePointApplication?.sample} />

        </section>


      </main>

      <footer>
        <Button icon={Check} label={t("Valider")} variant="success" action={onAccept} />
        <Button icon={Cross} label={t("Refuser")} variant="danger" action={onReject} />
        <Button icon={Download} label={t("Télécharger l'échantillon")} variant="primary" action={onDownloadSample} />
      </footer>
    </>
  )
}




export default ChargingPointsApplicationDetailsInProgress
