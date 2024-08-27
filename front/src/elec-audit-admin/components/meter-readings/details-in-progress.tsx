import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { AlertCircle, Check, Cross, Download } from "common/components/icons"
import { ElecMeterReadingsApplicationDetails } from "elec/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import SampleSummary from "../sample/details-sample-summary"
import ChargePointsSampleMap from "../sample/sample-map"
import ApplicationSummary from "./details-application-summary"
import Alert from "common/components/alert"

interface MeterReadingsApplicationDetailsInProgressProps {
  meterReadingsApplication: ElecMeterReadingsApplicationDetails | undefined
  onAccept: (force?: boolean) => void
  onReject: (force?: boolean) => void
  onDownloadSample: () => void
}
export const MeterReadingsApplicationDetailsInProgress = ({
  meterReadingsApplication,
  onAccept,
  onReject,
  onDownloadSample,
}: MeterReadingsApplicationDetailsInProgressProps) => {
  const { t } = useTranslation()
  const [confirmCheckbox, setConfirmCheckbox] = useState(false)

  return (
    <>
      <main>
        <section>
          <ApplicationSummary application={meterReadingsApplication} />
        </section>
        <Divider />
        {meterReadingsApplication?.sample && (
          <section>
            <SampleSummary sample={meterReadingsApplication?.sample} />
            <ChargePointsSampleMap chargePoints={meterReadingsApplication?.sample?.charge_points} />
            <Button icon={Download} label={t("Télécharger l'échantillon")} variant="secondary" action={onDownloadSample} />
          </section>
        )}
        <section>
          <Alert icon={AlertCircle} variant="warning" multiline label={t("L'échantillon a été reçu par l'auditeur. Vous serez informé par email lorsque ce dernier aura complété le rapport d'audit sur son espace sur Carbure.")} />
        </section>
        <section>
          <Checkbox
            value={confirmCheckbox}
            onChange={setConfirmCheckbox}
            label={t("Je confirme avoir reçu le résultat d'audit ou souhaite valider sans audit.")}
          />
        </section>
      </main>

      <footer>
        <Button
          icon={Check}
          label={t("Valider")}
          variant="success"
          action={onAccept}
          disabled={!confirmCheckbox}
        />
        <Button
          icon={Cross}
          label={t("Refuser")}
          variant="danger"
          action={onReject}
          disabled={!confirmCheckbox}
        />
      </footer>
    </>
  )
}

export default MeterReadingsApplicationDetailsInProgress
