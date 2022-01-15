import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import Checkbox from "common-v2/components/checkbox"
import Collapse from "common-v2/components/collapse"
import { AlertTriangle } from "common-v2/components/icons"
import { LoaderOverlay } from "common-v2/components/scaffold"
import { useMutation } from "common-v2/hooks/async"
import { getAnomalyText } from "lot-details/components/anomalies"
import { Lot, LotError } from "transactions/types"
import * as api from "../api"

export interface WarningAnomaliesProps {
  lot: Lot
  anomalies: LotError[]
}

export const WarningAnomalies = ({ lot, anomalies }: WarningAnomaliesProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const ackWarning = useMutation(
    (anomaly: LotError) => api.toggleWarning(entity.id, lot.id, anomaly.error),
    { invalidates: ["control-details"] }
  )

  return (
    <Collapse
      variant="warning"
      icon={AlertTriangle}
      label={`${t("Remarques")} (${anomalies.length})`}
    >
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
                value={anomaly.acked_by_admin}
                onChange={() => ackWarning.execute(anomaly)}
                style={{ opacity: anomaly.acked_by_admin ? 0.5 : 1 }}
              />
            </li>
          ))}
        </ul>
      </footer>

      {ackWarning.loading && <LoaderOverlay />}
    </Collapse>
  )
}
