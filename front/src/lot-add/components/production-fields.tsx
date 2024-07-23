import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import { Fieldset, useBind, useFormContext } from "common/components/form"
import {
	DateInput,
	DateInputProps,
	TextInput,
	TextInputProps,
} from "common/components/input"
import * as api from "carbure/api"
import * as norm from "carbure/utils/normalizers"
import { LotFormValue } from "./lot-form"
import { UserCheck } from "common/components/icons"
import { Entity, Country, ProductionSite } from "carbure/types"
import CertificateIcon from "transaction-details/components/lots/certificate"
import { compact, uniqueBy } from "common/utils/collection"

interface ProductionFieldsProps {
	readOnly?: boolean
}

export const ProductionFields = (props: ProductionFieldsProps) => {
	const { t } = useTranslation()

	return (
		<Fieldset label={t("Production")}>
			<ProducerField {...props} />
			<ProductionSiteField {...props} />
			<ProductionSiteCertificateField {...props} />
			<ProductionSiteDoubleCountingCertificateField {...props} />
			<ProductionCountryField {...props} />
			<ProductionSiteCommissioningDateField {...props} />
		</Fieldset>
	)
}

export const ProducerField = (props: AutocompleteProps<Entity | string>) => {
	const { t } = useTranslation()
	const entity = useEntity()
	const bind = useBind<LotFormValue>()

	const { value: producer, ...bound } = bind("producer")
	const isKnown = producer instanceof Object

	if (entity.isAdmin) {
		return (
			<Autocomplete
				label={t("Producteur")}
				value={producer}
				icon={isKnown ? UserCheck : undefined}
				create={norm.identity}
				defaultOptions={producer ? [producer] : undefined}
				getOptions={api.findProducers}
				normalize={norm.normalizeEntityOrUnknown}
				{...bound}
				{...props}
			/>
		)
	}

	// for entities that aren't producers, only show a simple text input to type an unknown producer
	if (!entity.isProducer) {
		return (
			<TextInput
				label={t("Producteur")}
				icon={isKnown ? UserCheck : undefined}
				value={isKnown ? producer.name : producer}
				{...bound}
				{...(props as TextInputProps)}
			/>
		)
	}

	const defaultOptions = uniqueBy(
		compact([producer, entity]),
		(v) => norm.normalizeEntityOrUnknown(v).label
	)

	return (
		<Autocomplete
			label={t("Producteur")}
			value={producer}
			icon={isKnown ? UserCheck : undefined}
			create={norm.identity}
			defaultOptions={defaultOptions}
			normalize={norm.normalizeEntityOrUnknown}
			{...bound}
			{...props}
			disabled={(!entity.has_trading && !entity.has_stocks) || bound.disabled}
		/>
	)
}

export const ProductionSiteField = (
	props: AutocompleteProps<ProductionSite | string>
) => {
	const { t } = useTranslation()
	const { value, bind } = useFormContext<LotFormValue>()

	const { value: productionSite, ...bound } = bind("production_site")
	const isKnown = productionSite instanceof Object

	const producer = value.producer instanceof Object ? value.producer.id : undefined // prettier-ignore

	// for unknown producers, we show a simple input to type unknown production sites
	if (producer === undefined) {
		return (
			<TextInput
				label={t("Site de production")}
				icon={isKnown ? UserCheck : undefined}
				value={isKnown ? productionSite.name : productionSite}
				{...bound}
				{...(props as TextInputProps)}
			/>
		)
	}

	// otherwise autocomplete the producer's production sites
	return (
		<Autocomplete
			required
			label={t("Site de production")}
			value={productionSite}
			icon={isKnown ? UserCheck : undefined}
			defaultOptions={isKnown ? [productionSite] : undefined}
			getOptions={(query) => api.findProductionSites(query, producer)}
			normalize={norm.normalizeProductionSiteOrUnknown}
			{...bound}
			{...props}
		/>
	)
}

export const ProductionSiteCertificateField = (
	props: AutocompleteProps<string>
) => {
	const { t } = useTranslation()
	const entity = useEntity()
	const { value, bind } = useFormContext<LotFormValue>()
	const bound = bind("production_site_certificate")

	const production_site_id =
		value.production_site instanceof Object
			? value.production_site.id
			: undefined

	const certificate =
		value.certificates?.production_site_certificate ?? undefined

	// if the production site is known, only propose its own certificates
	return (
		<Autocomplete
			icon={<CertificateIcon certificate={certificate} />}
			label={t("Certificat du site de production")}
			defaultOptions={bound.value ? [bound.value] : undefined}
			getOptions={(query) =>
				production_site_id !== undefined
					? api.findMyCertificates(query, {
							entity_id: entity.id,
							production_site_id,
						})
					: api.findCertificates(query)
			}
			{...bound}
			{...props}
		/>
	)
}

export const ProductionSiteDoubleCountingCertificateField = (
	props: TextInputProps
) => {
	const { t } = useTranslation()
	const { value, bind } = useFormContext<LotFormValue>()
	const entity = useEntity()
	const isAdminEditing = value.lot === undefined && entity.isAdmin

	// hide field for non-DC feedstocks
	if (!value.feedstock?.is_double_compte && !isAdminEditing) {
		return null
	}

	const bound = bind("production_site_double_counting_certificate")
	// if the production site is known, use its DC data instead of expecting manual input
	const dcProps =
		value.production_site instanceof Object
			? {
					...props,
					disabled: true,
					error: bound.error,
					value:
						value.production_site_double_counting_certificate ||
						value.production_site.dc_reference ||
						t("détection..."),
				}
			: { ...props, ...bound }

	const certificate =
		value.certificates?.production_site_double_counting_certificate ?? undefined

	return (
		<TextInput
			icon={<CertificateIcon certificate={certificate} />}
			label={t("Certificat double-comptage")}
			{...dcProps}
		/>
	)
}

export const ProductionCountryField = (props: AutocompleteProps<Country>) => {
	const { t } = useTranslation()
	const { value, bind } = useFormContext<LotFormValue>()
	const bound = bind("production_country")

	if (value.production_site instanceof Object) {
		return (
			<TextInput
				disabled
				readOnly={props.readOnly}
				label={t("Pays de production")}
				value={norm.normalizeCountry(value.production_site.country).label}
				error={bound.error}
			/>
		)
	}

	return (
		<Autocomplete
			label={t("Pays de production")}
			defaultOptions={bound.value ? [bound.value] : undefined}
			getOptions={api.findCountries}
			normalize={norm.normalizeCountry}
			{...bound}
			{...props}
		/>
	)
}

export const ProductionSiteCommissioningDateField = (props: DateInputProps) => {
	const { t } = useTranslation()
	const { value, bind } = useFormContext<LotFormValue>()
	const bound = bind("production_site_commissioning_date")

	const dateProps =
		value.production_site instanceof Object
			? { ...props, disabled: true, error: bound.error, value: value.production_site.date_mise_en_service } // prettier-ignore
			: { ...props, ...bound, required: true }

	return <DateInput label={t("Date de mise en service")} {...dateProps} />
}

export default ProductionFields
