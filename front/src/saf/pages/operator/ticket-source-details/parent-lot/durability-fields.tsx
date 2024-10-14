import { Fieldset } from "common/components/form"
import { NumberInput, TextInput } from "common/components/input"
import { formatGHG, formatPercentage } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafTicketSourceDetails } from "../../types"

const DurabilityFields = ({
  ticketSource,
}: {
  ticketSource: SafTicketSourceDetails
}) => {
  const { t } = useTranslation()

  return (
    <>
      <Fieldset small label={t("Émissions")}>
        <NumberInput
          hasTooltip
          label="EEC"
          title={t("Émissions résultant de l'extraction ou de la culture des matières premières")} // prettier-ignore
          value={ticketSource.eec}
          readOnly
        />
        <NumberInput
          hasTooltip
          label="EL"
          title={t("Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols")} // prettier-ignore
          value={ticketSource.el}
          readOnly
        />
        <NumberInput
          required
          hasTooltip
          label="EP"
          title={t("Émissions résultant dela transformation")}
          value={ticketSource.ep}
          readOnly
        />
        <NumberInput
          required
          hasTooltip
          label="ETD"
          title={t("Émissions résultant du transport et de la distribution")}
          value={ticketSource.etd}
          readOnly
        />
        <NumberInput
          label="EU"
          hasTooltip
          title={t("Émissions résultant du carburant à l'usage")}
          value={ticketSource.eu}
          readOnly
        />

        <TextInput
          readOnly
          hasTooltip
          label="Total"
          value={formatGHG(ticketSource.ghg_total ?? 0)}
        />
      </Fieldset>
      <Fieldset small label={t("Réductions")}>
        <NumberInput
          label="ESCA"
          hasTooltip
          title={t("Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole")} // prettier-ignore
          value={ticketSource.esca}
          readOnly
        />
        <NumberInput
          label="ECCS"
          hasTooltip
          title={t("Réductions d'émissions dues au piégeage et au stockage géologique du carbone")} // prettier-ignore
          value={ticketSource.eccs}
          readOnly
        />
        <NumberInput
          label="ECCR"
          hasTooltip
          title={t("Réductions d'émissions dues au piégeage et à la substitution du carbone")} // prettier-ignore
          value={ticketSource.eccr}
          readOnly
        />
        <NumberInput
          label="EEE"
          hasTooltip
          title={t("Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération")} // prettier-ignore
          value={ticketSource.eee}
          readOnly
        />

        <TextInput
          readOnly
          hasTooltip
          label={t("Réduction")}
          value={formatPercentage(ticketSource.ghg_reduction ?? 0)}
        />
      </Fieldset>
    </>
  )
}

export default DurabilityFields
