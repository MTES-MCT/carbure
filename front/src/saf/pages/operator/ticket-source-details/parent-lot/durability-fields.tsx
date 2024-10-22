import { Fieldset } from "common/components/form"
import { TextInput } from "common/components/input"
import {
  formatGHG,
  formatNumber,
  formatPercentage,
} from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafDurability } from "saf/types"

const formatNumberToText = (value: number | undefined) =>
  value ? formatNumber(value) : ""
const DurabilityFields = ({ durability }: { durability: SafDurability }) => {
  const { t } = useTranslation()

  return (
    <>
      <Fieldset small label={t("Émissions")}>
        <TextInput
          hasTooltip
          label="EEC"
          title={t("Émissions résultant de l'extraction ou de la culture des matières premières")} // prettier-ignore
          value={formatNumberToText(durability.eec)}
          readOnly
        />
        <TextInput
          hasTooltip
          label="EL"
          title={t("Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols")} // prettier-ignore
          value={formatNumberToText(durability.el)}
          readOnly
        />
        <TextInput
          required
          hasTooltip
          label="EP"
          title={t("Émissions résultant dela transformation")}
          value={formatNumberToText(durability.ep)}
          readOnly
        />
        <TextInput
          required
          hasTooltip
          label="ETD"
          title={t("Émissions résultant du transport et de la distribution")}
          value={formatNumberToText(durability.etd)}
          readOnly
        />
        <TextInput
          label="EU"
          hasTooltip
          title={t("Émissions résultant du carburant à l'usage")}
          value={formatNumberToText(durability.eu)}
          readOnly
        />

        <TextInput
          readOnly
          hasTooltip
          label="Total"
          value={formatGHG(durability.ghg_total ?? 0)}
        />
      </Fieldset>
      <Fieldset small label={t("Réductions")}>
        <TextInput
          label="ESCA"
          hasTooltip
          title={t("Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole")} // prettier-ignore
          value={formatNumberToText(durability.esca)}
          readOnly
        />
        <TextInput
          label="ECCS"
          hasTooltip
          title={t("Réductions d'émissions dues au piégeage et au stockage géologique du carbone")} // prettier-ignore
          value={formatNumberToText(durability.eccs)}
          readOnly
        />
        <TextInput
          label="ECCR"
          hasTooltip
          title={t("Réductions d'émissions dues au piégeage et à la substitution du carbone")} // prettier-ignore
          value={formatNumberToText(durability.eccr)}
          readOnly
        />
        <TextInput
          label="EEE"
          hasTooltip
          title={t("Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération")} // prettier-ignore
          value={formatNumberToText(durability.eee)}
          readOnly
        />

        <TextInput
          readOnly
          hasTooltip
          label={t("Réduction")}
          value={formatPercentage(durability.ghg_reduction ?? 0)}
        />
      </Fieldset>
    </>
  )
}

export default DurabilityFields
