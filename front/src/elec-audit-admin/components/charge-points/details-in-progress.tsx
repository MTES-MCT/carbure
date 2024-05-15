import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { Check, Cross, Download } from "common/components/icons"
import { ElecChargePointsApplicationDetails } from "elec/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import ApplicationSummary from "./details-application-summary"
import SampleSummary from "./details-sample-summary"
import ChargePointsSampleMap from "./sample-map"




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
  const [confirmCheckbox, setConfirmCheckbox] = useState(false)

  return (
    <>
      <main>
        <section>
          <ApplicationSummary application={chargePointApplication} />
        </section>
        <Divider />
        {chargePointApplication?.sample && (
          <section>
            <SampleSummary sample={chargePointApplication?.sample} />
            <ChargePointsSampleMap chargePoints={chargePointApplication?.sample?.charge_points} />
            <Button icon={Download} label={t("Télécharger l'échantillon")} variant="secondary" action={onDownloadSample} style={{ width: "min-content" }} />
          </section>
        )}
        <section>
          <Checkbox
            value={confirmCheckbox}
            onChange={setConfirmCheckbox}
            label={t("Je confirme avoir reçu le résultat d'audit de la part de l'auditeur par e-mail afin de valider ou refuser l'inscription de ces points de charge.")}
          />
        </section>
      </main>

      <footer>
        <Button icon={Check} label={t("Valider")} variant="success" action={onAccept} disabled={!confirmCheckbox} />
        <Button icon={Cross} label={t("Refuser")} variant="danger" action={onReject} disabled={!confirmCheckbox} />
      </footer>
    </>
  )
}


export default ChargingPointsApplicationDetailsInProgress
