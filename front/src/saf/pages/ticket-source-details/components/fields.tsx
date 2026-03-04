import * as norm from "common/utils/normalizers"
import cl from "clsx"
import { formatDate, formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import css from "common/components/form.module.css"
import { SafTicketSourceDetails } from "saf/types"
import DurabilityFields from "saf/components/durability-fields"
import { TextInput, DateInput } from "common/components/inputs2"
import { Dialog } from "common/components/dialog2"

interface TicketSourceFieldsProps {
  ticketSource: SafTicketSourceDetails | undefined
}
export const TicketSourceFields = ({
  ticketSource,
}: TicketSourceFieldsProps) => {
  const { t } = useTranslation()

  if (!ticketSource) return null

  return (
    <div className={cl(css.form, css.columns)}>
      <Dialog.Section label={t("Lot")}>
        <TextInput
          label={t("Lot d'origine (Carbure)")}
          value={ticketSource.origin_lot?.carbure_id ?? "N/A"}
          readOnly
        />
        <TextInput
          label={t("Volume")}
          value={`${formatNumber(ticketSource.total_volume)} L`}
          readOnly
        />
        <TextInput
          label={t("Biocarburant")}
          value={ticketSource.biofuel.code ?? "-"}
          readOnly
        />
        <TextInput
          label={t("Matière première")}
          value={ticketSource.feedstock.name ?? "-"}
          readOnly
        />
        <TextInput
          label={t("Pays d'origine")}
          value={
            norm.normalizeCountry(ticketSource.country_of_origin).label ?? "-"
          }
          readOnly
        />
        <TextInput
          label={t("Date de livraison")}
          value={
            ticketSource.parent_lot?.delivery_date
              ? formatDate(ticketSource.parent_lot?.delivery_date)
              : t("N/A")
          }
          readOnly
        />
        {ticketSource.origin_lot_site && (
          <TextInput
            readOnly
            label={t("Dépôt du lot d'origine")}
            value={ticketSource.origin_lot_site.name}
          />
        )}
        {ticketSource.origin_lot?.pos_number && (
          <TextInput
            readOnly
            label={t("N˚ de POS (hors Carbure)")}
            value={ticketSource.origin_lot?.pos_number}
          />
        )}
      </Dialog.Section>
      <Dialog.Section label={t("Production")}>
        <TextInput
          label={t("Producteur")}
          value={
            ticketSource.carbure_producer?.name ||
            ticketSource.unknown_producer ||
            t("Inconnu")
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
          label={t("Pays de production")}
          value={
            ticketSource.carbure_production_site
              ? norm.normalizeCountry(ticketSource.country_of_origin).label
              : t("Inconnu")
          }
          readOnly
        />
        <DateInput
          label={t("Date de mise en service")}
          value={ticketSource.production_site_commissioning_date ?? ""}
          readOnly
        />
      </Dialog.Section>
      <DurabilityFields durability={ticketSource} />
    </div>
  )
}

export default TicketSourceFields
