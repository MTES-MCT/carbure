import { useState } from "react"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { CheckboxGroup } from "common-v2/components/checkbox"
import Collapse from "common-v2/components/collapse"
import { AlertTriangle } from "common-v2/components/icons"
import { useMutation } from "common-v2/hooks/async"
import { normalizeAnomaly } from "lot-details/components/anomalies"
import { Lot, LotError } from "transactions/types"
import pickApi from "../api"

export interface WarningAnomaliesProps {
  lot: Lot
  anomalies: LotError[]
}

export const WarningAnomalies = ({ lot, anomalies }: WarningAnomaliesProps) => {
  const { t } = useTranslation()

  const entity = useEntity()
  const api = pickApi(entity)

  const ackWarning = useMutation((error: string) =>
    api.toggleWarning(entity.id, lot.id, error)
  )

  const [checked, setChecked] = useState<string[] | undefined>(
    anomalies.filter((a) => a.acked_by_admin).map((a) => a.error)
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
        <CheckboxGroup
          variant="opacity"
          value={checked}
          options={anomalies}
          onChange={setChecked}
          onToggle={(error) => ackWarning.execute(error)}
          normalize={normalizeAnomaly}
        />
      </footer>
    </Collapse>
  )
}
