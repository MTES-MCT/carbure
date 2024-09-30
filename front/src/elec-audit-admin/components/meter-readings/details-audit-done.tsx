import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { Check, Cross } from "common/components/icons"
import { ElecMeterReadingsApplicationDetails } from "elec/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import SampleDetailsAuditDoneSection from "../sample/details-sample-audit-done-section"
import ApplicationSummary from "./details-application-summary"

interface MeterReadingsApplicationDetailsAuditDoneProps {
  meterReadingsApplication: ElecMeterReadingsApplicationDetails | undefined
  onAccept: (force?: boolean) => void
  onReject: (force?: boolean) => void
  onDownloadSample: () => void
}
export const MeterReadingsApplicationDetailsAuditDone = ({
  meterReadingsApplication,
  onAccept,
  onReject,
  onDownloadSample,
}: MeterReadingsApplicationDetailsAuditDoneProps) => {
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
          <SampleDetailsAuditDoneSection
            sample={meterReadingsApplication.sample}
            onDownloadSample={onDownloadSample}
          />
        )}
        <section>
          <Checkbox
            value={confirmCheckbox}
            onChange={setConfirmCheckbox}
            label={t(
              "Je confirme avoir téléchargé et verifié le résultat d'audit afin de valider les relevés trimestriels des points de recharge ci-dessus."
            )}
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

export default MeterReadingsApplicationDetailsAuditDone
