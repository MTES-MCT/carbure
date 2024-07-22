import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { Check, Cross, Download } from "common/components/icons"
import { ElecMeterReadingsApplicationDetails } from "elec/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import SampleSummary from "../sample/details-sample-summary"
import ChargePointsSampleMap from "../sample/sample-map"
import ApplicationSummary from "./details-application-summary"




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
  onDownloadSample
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
          <Checkbox
            value={confirmCheckbox}
            onChange={setConfirmCheckbox}
            label={t("Je confirme avoir reçu le résultat d'audit de la part de l'auditeur par e-mail afin de valider ou refuser le relevé T{{quarter}} {{year}}.", {
              quarter: meterReadingsApplication?.quarter,
              year: meterReadingsApplication?.year,
            })}
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


export default MeterReadingsApplicationDetailsInProgress
