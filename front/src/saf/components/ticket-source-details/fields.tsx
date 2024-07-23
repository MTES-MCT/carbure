import * as norm from "carbure/utils/normalizers"
import cl from "clsx"
import { Fieldset } from "common/components/form"
import { DateInput, TextInput } from "common/components/input"
import { formatDate, formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import css from "../../../common/components/form.module.css"
import { SafTicketSourceDetails } from "../../types"
import DurabilityFields from "../durability-fields"

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
				<TextInput
					label={t("Date de livraison")}
					value={
						ticketSource.parent_lot?.delivery_date
							? formatDate(ticketSource.parent_lot?.delivery_date)
							: t("N/A")
					}
					readOnly
				/>
			</Fieldset>
			<Fieldset label={t("Production")}>
				<TextInput
					label={t("Producteur")}
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
					value={ticketSource.production_site_commissioning_date}
					readOnly
				/>
			</Fieldset>
			<DurabilityFields durability={ticketSource} />
		</div>
	)
}

export default TicketSourceFields
