import { useTranslation } from "react-i18next"
import { Lot, LotError } from "transactions/types"
import Collapse from "common-v2/components/collapse"
import { AlertOctagon, AlertTriangle } from "common-v2/components/icons"
import Checkbox from "common-v2/components/checkbox"
import i18next from "i18next"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { LoaderOverlay } from "common-v2/components/scaffold"
import * as api from "../api"

export interface BlockingAnomaliesProps {
  anomalies: LotError[]
}

export const BlockingAnomalies = ({ anomalies }: BlockingAnomaliesProps) => {
  const { t } = useTranslation()
  return (
    <Collapse
      variant="danger"
      icon={AlertOctagon}
      label={`${t("Erreurs")} (${anomalies.length})`}
    >
      <section>
        {t(
          "Vous ne pouvez pas valider ce lot tant que les problèmes suivants n'ont pas été adressés :"
        )}
      </section>

      <footer>
        <ul>
          {anomalies.map((anomaly, i) => (
            <li key={i}>{getAnomalyText(anomaly)}</li>
          ))}
        </ul>
      </footer>
    </Collapse>
  )
}

export interface WarningAnomaliesProps {
  lot: Lot
  anomalies: LotError[]
}

export const WarningAnomalies = ({ lot, anomalies }: WarningAnomaliesProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const isCreator = lot.added_by?.id === entity.id
  const isRecipient = lot.carbure_client?.id === entity.id

  const ackWarning = useMutation(
    (anomaly: LotError) => api.ackWarning(entity.id, lot.id, anomaly.error),
    { invalidates: ["lot-details"] }
  )

  function isAcked(anomaly: LotError) {
    if (isCreator) return anomaly.acked_by_creator
    else if (isRecipient) return anomaly.acked_by_recipient
    else return false
  }

  return (
    <Collapse
      variant="warning"
      icon={AlertTriangle}
      label={`${t("Remarques")} (${anomalies.length})`}
    >
      <section>
        {t(
          "Des incohérences potentielles ont été détectées, elles n'empêchent pas la validation du lot mais peuvent donner lieu à un contrôle."
        )}
      </section>
      <section>
        {t(
          "Si vous souhaitez ignorer certaines de ces remarques, vous pouvez cocher la case correspondante. Lorsque toutes les cases sont cochées, le lot n'apparait plus comme incohérent sur CarbuRe."
        )}
      </section>

      <footer>
        <ul
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 8,
            paddingLeft: 8,
            listStyle: "none",
          }}
        >
          {anomalies.map((anomaly, i) => (
            <li key={i}>
              <Checkbox
                label={getAnomalyText(anomaly)}
                value={isAcked(anomaly)}
                onChange={() => ackWarning.execute(anomaly)}
                style={{ opacity: isAcked(anomaly) ? 0.5 : 1 }}
              />
            </li>
          ))}
        </ul>
      </footer>

      {ackWarning.loading && <LoaderOverlay />}
    </Collapse>
  )
}

function getAnomalyText(anomaly: LotError) {
  const error = i18next.t(anomaly.error, { ns: "errors" }) || i18next.t("Erreur de validation") // prettier-ignore
  const extra = anomaly.extra && anomaly.extra !==  i18next.t(anomaly.error, { ns: "errors" }) ? ` - ${anomaly.extra}` : '' // prettier-ignore
  return error + extra
}

export function separateAnomalies(anomalies: LotError[]) {
  return [
    anomalies.filter((anomaly) => anomaly.is_blocking),
    anomalies.filter((anomaly) => !anomaly.is_blocking),
  ]
}
