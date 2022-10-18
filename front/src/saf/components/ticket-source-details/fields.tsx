import { Fieldset } from "common/components/form"
import { DateInput, NumberInput, TextInput } from "common/components/input"
import {
  formatGHG,
  formatNumber,
  formatPercentage,
} from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafDurability, SafTicketSourceDetails } from "../../types"
import cl from "clsx"
import css from "../../../common/components/form.module.css"
import * as norm from "carbure/utils/normalizers"

interface TicketSourceFieldsProps {
  ticketSource: SafTicketSourceDetails
}
export const TicketSourceFields = ({
  ticketSource,
}: TicketSourceFieldsProps) => {
  const { t } = useTranslation()

  const production_site_name = ticketSource.carbure_production_site

  return (
    <div className={cl(css.form, css.columns)}>
      <Fieldset label={t("Lot")}>
        <TextInput
          label={t("Volume")}
          value={`${formatNumber(ticketSource.total_volume)} L`}
          readOnly
        />
        <TextInput
          label={t("Biocarburant")}
          value={ticketSource.biofuel.code}
          readOnly
        />
        <TextInput
          label={t("Matière première")}
          value={ticketSource.feedstock.name}
          readOnly
        />
        <TextInput
          label={t("Pays d'origine")}
          value={norm.normalizeCountry(ticketSource.country_of_origin).label}
          readOnly
        />
      </Fieldset>
      <Fieldset label={t("Producteur")}>
        <TextInput
          label={t("Production")}
          value={
            ticketSource.carbure_producer?.name ??
            ticketSource.unknown_producer ??
            ""
          }
          readOnly
        />
        <TextInput
          label={t("Site de production")}
          value={
            ticketSource.carbure_production_site
              ? ticketSource.carbure_production_site.name
              : t("Inconnu")
          }
          readOnly
        />
        <TextInput
          label={t("Pays de Production")}
          value={
            ticketSource.carbure_production_site
              ? norm.normalizeCountry(ticketSource.country_of_origin).label
              : t("Inconnu")
          }
          readOnly
        />
        <DateInput
          label={t("Date de mise en service")}
          value={ticketSource.production_site_commissioning_date}
          readOnly
        />
      </Fieldset>
      <DurabilityFields durability={ticketSource} />
    </div>
  )
}

export default TicketSourceFields

const DurabilityFields = ({ durability }: { durability: SafDurability }) => {
  const { t } = useTranslation()

  return (
    <>
      <Fieldset small label={t("Émissions")}>
        <NumberInput
          label="EEC"
          title={t("Émissions résultant de l'extraction ou de la culture des matières premières")} // prettier-ignore
          value={durability.eec}
          readOnly
        />
        <NumberInput
          label="EL"
          title={t("Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols")} // prettier-ignore
          value={durability.el}
          readOnly
        />
        <NumberInput
          required
          label="EP"
          title={t("Émissions résultant dela transformation")}
          value={durability.ep}
          readOnly
        />
        <NumberInput
          required
          label="ETD"
          title={t("Émissions résultant du transport et de la distribution")}
          value={durability.etd}
          readOnly
        />
        <NumberInput
          label="EU"
          title={t("Émissions résultant du carburant à l'usage")}
          value={durability.eu}
          readOnly
        />

        <TextInput
          readOnly
          label="Total"
          value={formatGHG(durability.ghg_total ?? 0)}
        />
      </Fieldset>
      <Fieldset small label={t("Réductions")}>
        <NumberInput
          label="ESCA"
          title={t("Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole")} // prettier-ignore
          value={durability.esca}
          readOnly
        />
        <NumberInput
          label="ECCS"
          title={t("Réductions d'émissions dues au piégeage et au stockage géologique du carbone")} // prettier-ignore
          value={durability.eccs}
          readOnly
        />
        <NumberInput
          label="ECCR"
          title={t("Réductions d'émissions dues au piégeage et à la substitution du carbone")} // prettier-ignore
          value={durability.eccr}
          readOnly
        />
        <NumberInput
          label="EEE"
          title={t("Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération")} // prettier-ignore
          value={durability.eee}
          readOnly
        />

        <TextInput
          readOnly
          label={t("Réduction")}
          value={formatPercentage(durability.ghg_reduction ?? 0)}
        />
      </Fieldset>
    </>
  )
}
