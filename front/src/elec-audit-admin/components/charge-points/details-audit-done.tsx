import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { Check, Cross, Download, Message } from "common/components/icons"
import { ElecChargePointsApplicationDetails } from "elec/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import ApplicationSummary from "./details-application-summary"
import SampleSummary from "../sample/details-sample-summary"
import ChargePointsSampleMap from "../sample/sample-map"
import * as api from "elec-audit-admin/api"
import { use } from "i18next"
import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"

interface ChargePointsApplicationDetailsAuditDoneProps {
  chargePointApplication: ElecChargePointsApplicationDetails | undefined
  onAccept: (force?: boolean) => void
  onReject: (force?: boolean) => void
  onDownloadSample: () => void
}
export const ChargePointsApplicationDetailsAuditDone = ({
  chargePointApplication,
  onAccept,
  onReject,
}: ChargePointsApplicationDetailsAuditDoneProps) => {
  const { t } = useTranslation()
  const [confirmCheckbox, setConfirmCheckbox] = useState(false)
  const entity = useEntity()

  const downloadAuditReport = async () => {
    return api.downloadAuditReport(entity.id, chargePointApplication?.sample?.application_id!)
  }

  // if (chargePointApplication?.sample) {
  //   chargePointApplication.sample.auditor_name = "Veritas"
  //   chargePointApplication.sample.comment_count = 2
  // }
  const commentCount = chargePointApplication?.sample?.comment_count
  const auditorName = chargePointApplication?.sample?.auditor_name
  return (
    <>
      <main>
        <section>
          <ApplicationSummary application={chargePointApplication} />
        </section>
        <Divider />

        <section>
          <SampleSummary sample={chargePointApplication?.sample} />
          <Divider />
          <strong>{t("Résultat d'audit")}</strong>
          <p>{t("Télécharger directement le fichier d'audit pour visualiser les informations entrées par l'auditeur.")}</p>
          <Button icon={Download} label={t("Télécharger le rapport d'audit")} variant="secondary" action={downloadAuditReport} />
        </section>
        {commentCount &&
          <section>
            <Alert icon={Message} variant="info" >
              <Trans defaults={"<b>{{ count }} points de charges </b>  ont été commentés par l'auditeur <b>{{auditorName}}</b> dans le fichier excel."} values={{ count: commentCount, auditorName }} />
            </Alert>
          </section>
        }
        <section>
          <Checkbox
            value={confirmCheckbox}
            onChange={setConfirmCheckbox}
            label={t(
              "Je confirme avoir téléchargé et verifié le résultat d'audit afin de valider l'inscription des points de recharge ci-dessus."
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

export default ChargePointsApplicationDetailsAuditDone
