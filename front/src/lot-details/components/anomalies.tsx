import { useTranslation } from "react-i18next"
import { Lot, LotError } from "transactions/types"
import Collapse from "common-v2/components/collapse"
import {
  AlertOctagon,
  AlertTriangle,
  Eye,
  EyeOff,
} from "common-v2/components/icons"
import { CheckboxGroup } from "common-v2/components/checkbox"
import i18next from "i18next"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import * as api from "../api"
import { Normalizer } from "common-v2/utils/normalize"
import { useState } from "react"
import Button from "common-v2/components/button"
import { UserRole } from "carbure/types"

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

  function isAcked(anomaly: LotError) {
    if (isCreator) return anomaly.acked_by_creator
    else if (isRecipient) return anomaly.acked_by_recipient
    else return false
  }

  const [checked, setChecked] = useState<string[] | undefined>(
    anomalies.filter(isAcked).map((a) => a.error)
  )

  const ackWarning = useMutation(
    (errors: string[]) => api.toggleWarning(entity.id, lot.id, errors),
    { invalidates: [] }
  )

  const hasEditRights = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)
  const isAllChecked = anomalies.every((a) => checked?.includes(a.error))

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

      {hasEditRights && (
        <section>
          {t(
            "Si vous souhaitez ignorer certaines de ces remarques, vous pouvez cocher la case correspondante. Lorsque toutes les cases sont cochées, le lot n'apparait plus comme incohérent sur CarbuRe."
          )}
        </section>
      )}

      <section>
        {hasEditRights && (
          <CheckboxGroup
            variant="opacity"
            value={checked}
            options={anomalies}
            onChange={setChecked}
            onToggle={(error) => ackWarning.execute([error])}
            normalize={normalizeAnomaly}
          />
        )}
        {!hasEditRights && (
          <ul>
            {anomalies.map((anomaly, i) => (
              <li key={i}>{getAnomalyText(anomaly)}</li>
            ))}
          </ul>
        )}
      </section>

      <footer>
        {hasEditRights && (
          <Button
            icon={isAllChecked ? Eye : EyeOff}
            loading={ackWarning.loading}
            label={
              isAllChecked
                ? t("Rétablir toutes ces remarques")
                : t("Ignorer toutes ces remarques")
            }
            action={() => {
              const errors = anomalies.map((a) => a.error)
              ackWarning.execute(errors)
              setChecked(isAllChecked ? [] : errors)
            }}
          />
        )}
      </footer>
    </Collapse>
  )
}

export const normalizeAnomaly: Normalizer<LotError, string> = (anomaly) => ({
  value: anomaly.error,
  label: getAnomalyText(anomaly),
})

export function getAnomalyText(anomaly: LotError) {
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
