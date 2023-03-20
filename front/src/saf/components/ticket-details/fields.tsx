import { Fieldset } from "common/components/form"
import { DateInput, NumberInput, TextInput } from "common/components/input"
import {
  formatDate,
  formatGHG,
  formatNumber,
  formatPercentage,
  formatPeriod,
} from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import {
  SafDurability,
  SafTicketDetails,
  SafTicketSourceDetails,
} from "../../types"
import cl from "clsx"
import css from "../../../common/components/form.module.css"
import * as norm from "carbure/utils/normalizers"
import DurabilityFields from "../durability-fields"

interface TicketFieldsProps {
  ticket: SafTicketDetails | undefined
}
export const TicketFields = ({ ticket }: TicketFieldsProps) => {
  const { t } = useTranslation()

  if (!ticket) return null

  console.log(
    "norm.normalizeBiofuel(ticket.biofuel).label:",
    norm.normalizeBiofuel(ticket.biofuel)
  )
  return (
    <div className={cl(css.form, css.columns)}>
      <Fieldset label={t("Lot")}>
        <TextInput
          label={t("Volume")}
          value={`${formatNumber(ticket.volume)} L`}
          readOnly
        />
        <TextInput
          label={t("Biocarburant")}
          value={norm.normalizeBiofuel(ticket.biofuel).label}
          readOnly
        />
        <TextInput
          label={t("Matière première")}
          value={norm.normalizeFeedstock(ticket.feedstock).label}
          readOnly
        />
        <TextInput
          label={t("Pays d'origine")}
          value={norm.normalizeCountry(ticket.country_of_origin).label}
          readOnly
        />
      </Fieldset>
      <Fieldset label={t("Producteur")}>
        <TextInput
          label={t("Production")}
          value={ticket.carbure_producer?.name ?? ticket.unknown_producer ?? ""}
          readOnly
        />
        <TextInput
          label={t("Site de production")}
          value={
            ticket.carbure_production_site
              ? ticket.carbure_production_site.name
              : t("Inconnu")
          }
          readOnly
        />
        <TextInput
          label={t("Pays de production")}
          value={
            ticket.carbure_production_site
              ? norm.normalizeCountry(ticket.country_of_origin).label
              : t("Inconnu")
          }
          readOnly
        />
        <DateInput
          label={t("Date de mise en service")}
          value={ticket.production_site_commissioning_date}
          readOnly
        />
      </Fieldset>
      <Fieldset label={t("Affectation")}>
        <TextInput label={t("Fournisseur")} value={ticket.supplier} readOnly />
        <TextInput label={t("Client")} value={ticket.client} readOnly />
        <TextInput
          label={t("Période d'affectation")}
          value={formatPeriod(ticket.assignment_period)}
          readOnly
        />
        {ticket.free_field && (
          <TextInput
            label={t("Champ libre")}
            value={ticket.free_field}
            readOnly
          />
        )}
      </Fieldset>
      <DurabilityFields durability={ticket} />
    </div>
  )
}

export default TicketFields
