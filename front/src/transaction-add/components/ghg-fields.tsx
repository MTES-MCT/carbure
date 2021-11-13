import { useTranslation } from "react-i18next"
import isAfter from "date-fns/isAfter"
import { Fieldset, useFormContext } from "common-v2/components/form"
import { NumberInput, TextInput } from "common-v2/components/input"
import { LotFormValue } from "./form"
import { formatPercentage, formatGHG } from "common-v2/utils/formatters"

export const EmissionFields = () => {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<LotFormValue>()

  return (
    <Fieldset small label={t("Émissions")}>
      <NumberInput
        label="EEC"
        title={t("Émissions résultant de l'extraction ou de la culture des matières premières")} // prettier-ignore
        {...bind("eec")}
      />
      <NumberInput
        label="EL"
        title={t("Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols")} // prettier-ignore
        {...bind("el")}
      />
      <NumberInput
        label="EP"
        title={t("Émissions résultant dela transformation")}
        {...bind("ep")}
      />
      <NumberInput
        label="ETD"
        title={t("Émissions résultant du transport et de la distribution")}
        {...bind("etd")}
      />
      <NumberInput
        label="EU"
        title={t("Émissions résultant du carburant à l'usage")}
        {...bind("eu")}
      />

      <TextInput
        readOnly
        label="Total"
        value={formatGHG(value.ghg_total ?? 0)}
      />
    </Fieldset>
  )
}

// date where RED II took effect
const JULY_FIRST_21 = new Date("2021-07-01")

export const ReductionFields = () => {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<LotFormValue>()

  const date = new Date(value.delivery_date ?? "")
  const isRedII = isAfter(date, JULY_FIRST_21)

  return (
    <Fieldset small label={t("Réductions")}>
      <NumberInput
        label="ESCA"
        title={t("Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole")} // prettier-ignore
        {...bind("esca")}
      />
      <NumberInput
        label="EL"
        title={t("Réductions d'émissions dues au piégeage et au stockage géologique du carbone")} // prettier-ignore
        {...bind("eccs")}
      />
      <NumberInput
        label="EP"
        title={t("Réductions d'émissions dues au piégeage et à la substitution du carbone")} // prettier-ignore
        {...bind("eccr")}
      />
      <NumberInput
        label="EEE"
        title={t("Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération")} // prettier-ignore
        {...bind("eee")}
      />

      <TextInput
        asideY
        readOnly
        label={t("Réd. RED I")}
        value={formatPercentage(value.ghg_reduction ?? 0)}
      />
      {isRedII && (
        <TextInput
          readOnly
          label={t("Réd. RED II")}
          value={formatPercentage(value.ghg_reduction_red_ii ?? 0)}
        />
      )}
    </Fieldset>
  )
}
