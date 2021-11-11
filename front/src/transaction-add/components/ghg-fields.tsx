import { useTranslation } from "react-i18next"
import { Fieldset, useBind } from "common-v2/components/form"
import { NumberInput } from "common-v2/components/input"
import { LotFormValue } from "./form"

export const EmissionFields = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()

  return (
    <Fieldset small label={t("Émissions")}>
      <NumberInput label="EEC" {...bind("eec")} />
      <NumberInput label="EL" {...bind("el")} />
      <NumberInput label="EP" {...bind("ep")} />
      <NumberInput label="ETD" {...bind("etd")} />
      <NumberInput label="EU" {...bind("eu")} />

      <NumberInput readOnly label="Total" {...bind("ghg_total")} />
    </Fieldset>
  )
}

export const ReductionFields = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()

  return (
    <Fieldset small label={t("Réductions")}>
      <NumberInput label="ESCA" {...bind("esca")} />
      <NumberInput label="EL" {...bind("eccs")} />
      <NumberInput label="EP" {...bind("eccr")} />
      <NumberInput label="ETD" {...bind("eee")} />

      <NumberInput
        readOnly
        label="Réd RED I"
        {...bind("ghg_reduction")} // prettier-ignore
      />
      <NumberInput
        readOnly
        label="Réd RED II"
        {...bind("ghg_reduction_red_ii")}
      />
    </Fieldset>
  )
}
