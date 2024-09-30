import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { AlertCircle, Check, Cross, Download } from "common/components/icons"
import { ElecChargePointsApplicationDetails } from "elec/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import ApplicationSummary from "./details-application-summary"
import SampleSummary from "../sample/details-sample-summary"
import ChargePointsSampleMap from "../sample/sample-map"
import Alert from "common/components/alert"

interface ChargePointsApplicationDetailsInProgressProps {
  chargePointApplication: ElecChargePointsApplicationDetails | undefined
  onAccept: (force?: boolean) => void
  onReject: (force?: boolean) => void
  onDownloadSample: () => void
}
export const ChargePointsApplicationDetailsInProgress = ({
  chargePointApplication,
  onAccept,
  onReject,
  onDownloadSample,
}: ChargePointsApplicationDetailsInProgressProps) => {
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
            <ChargePointsSampleMap
              chargePoints={chargePointApplication?.sample?.charge_points}
            />
            <Button
              icon={Download}
              label={t("Télécharger l'échantillon")}
              variant="secondary"
              action={onDownloadSample}
            />
          </section>
        )}
        <section>
          <Alert
            icon={AlertCircle}
            variant="warning"
            multiline
            label={t(
              "L'échantillon a été reçu par l'auditeur. Vous serez informé par email lorsque ce dernier aura complété le rapport d'audit sur son espace sur Carbure."
            )}
          />
        </section>
        <section>
          <Checkbox
            value={confirmCheckbox}
            onChange={setConfirmCheckbox}
            label={t(
              "Je confirme avoir reçu le résultat d'audit ou souhaite valider sans audit."
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

export default ChargePointsApplicationDetailsInProgress
