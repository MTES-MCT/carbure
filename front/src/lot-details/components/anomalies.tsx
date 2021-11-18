import { useTranslation } from "react-i18next"
import { LotAnomaly } from "lot-details/types"
import Collapse from "common-v2/components/collapse"
import { AlertOctagon, AlertTriangle } from "common-v2/components/icons"

export interface AnomaliesProps {
  anomalies: LotAnomaly[]
}

export const Anomalies = ({ anomalies }: AnomaliesProps) => {
  const blocking = anomalies.filter((anomaly) => anomaly.is_blocking)
  const nonBlocking = anomalies.filter((anomaly) => !anomaly.is_blocking)

  return (
    <>
      {blocking.length > 0 && (
        <section>
          <BlockingAnomalies anomalies={blocking} />
        </section>
      )}
      {nonBlocking.length > 0 && (
        <section>
          <WarningAnomalies anomalies={nonBlocking} />
        </section>
      )}
    </>
  )
}

export const BlockingAnomalies = ({ anomalies }: AnomaliesProps) => {
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
            <Anomaly key={i} anomaly={anomaly} />
          ))}
        </ul>
      </footer>
    </Collapse>
  )
}

export const WarningAnomalies = ({ anomalies }: AnomaliesProps) => {
  const { t } = useTranslation()
  return (
    <Collapse
      variant="warning"
      icon={AlertTriangle}
      label={`${t("Remarques")} (${anomalies.length})`}
    >
      <section>
        {t(
          "Des incohérences potentielles ont été détectées, elles n'empêchent pas la validation du lot mais peuvent donner lieu à un contrôle :"
        )}
      </section>

      <footer>
        <ul>
          {anomalies.map((anomaly, i) => (
            <Anomaly key={i} anomaly={anomaly} />
          ))}
        </ul>
      </footer>
    </Collapse>
  )
}

export const Anomaly = ({ anomaly }: { anomaly: LotAnomaly }) => {
  const { t } = useTranslation()
  return (
    <li>
      {t(anomaly.error, { ns: "errors" }) || t("Erreur de validation")}{" "}
      {anomaly.extra &&
        anomaly.extra !== t(anomaly.error, { ns: "errors" }) &&
        ` - ${anomaly.extra}`}
    </li>
  )
}

export default Anomalies
