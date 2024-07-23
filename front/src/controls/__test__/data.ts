import { LotsUpdateResponse } from "controls/types"
import { LotError } from "transactions/types"

export const lotSummary = {
	count: 3,
	total_volume: 3743403.2,
	lots: [
		{
			supplier: "Blablabla",
			client: "Blebleble",
			biofuel_code: "ETH",
			volume_sum: 35554,
			avg_ghg_reduction: 78.16,
			total: 1,
			pending: 1,
		},
		{
			supplier: "Blebleble",
			client: "Blablabla",
			biofuel_code: "ETH",
			volume_sum: 29599.6,
			avg_ghg_reduction: 72.2,
			total: 1,
			pending: 1,
		},
		{
			supplier: "Blublublu",
			client: "Blebleble",
			biofuel_code: "ETH",
			volume_sum: 29599.6,
			avg_ghg_reduction: 72.2,
			total: 1,
			pending: 1,
		},
	],
}

export const lot = {
	id: 921883,
	year: 2022,
	period: 202207,
	carbure_id: "L202207-CZ-584-None",
	carbure_producer: null,
	unknown_producer: "",
	carbure_production_site: null,
	unknown_production_site: "",
	production_country: {
		name: "République tchèque",
		name_en: "Czech Republic",
		code_pays: "CZ",
	},
	production_site_commissioning_date: "2011-06-30",
	production_site_certificate: "",
	production_site_double_counting_certificate: "",
	carbure_supplier: {
		id: 90,
		name: "Cargill International Sa",
		entity_type: "Trader",
		has_mac: false,
		has_trading: true,
		has_direct_deliveries: true,
		has_stocks: true,
		preferred_unit: "l",
		legal_name: "",
		registration_id: "",
		sustainability_officer_phone_number: "",
		sustainability_officer: "",
		registered_address: "",
	},
	unknown_supplier: null,
	supplier_certificate: "EU-ISCC-Cert-DE105-81648311",
	supplier_certificate_type: null,
	transport_document_type: "OTHER",
	transport_document_reference: "22FRG8892500784698152",
	carbure_client: {
		id: 19,
		name: "CARFUEL",
		entity_type: "Opérateur",
		has_mac: false,
		has_trading: false,
		has_direct_deliveries: true,
		has_stocks: false,
		preferred_unit: "l",
		legal_name: "",
		registration_id: "",
		sustainability_officer_phone_number: "",
		sustainability_officer: "",
		registered_address: "",
	},
	unknown_client: "False",
	dispatch_date: null,
	carbure_dispatch_site: {
		id: 90,
		name: "ALKION TERMINAL MARSEILLE",
		city: "Lavera",
		depot_id: "1696",
		country: {
			name: "France",
			name_en: "France",
			code_pays: "FR",
		},
		depot_type: "EFS",
		address: "Route du port petrolier",
		postal_code: "13117",
		gps_coordinates: "43.401690, 4.999690",
		accise: null,
	},
	unknown_dispatch_site: null,
	dispatch_site_country: {
		name: "France",
		name_en: "France",
		code_pays: "FR",
	},
	delivery_date: "2022-07-02",
	carbure_delivery_site: {
		id: 71,
		name: "Dépôts Pétrolier de Fos - D.P.F",
		city: "Fos sur Mer",
		depot_id: "584",
		country: {
			name: "France",
			name_en: "France",
			code_pays: "FR",
		},
		depot_type: "EFS",
		address: "",
		postal_code: "13039",
		gps_coordinates: "43.434540, 4.916129",
		accise: null,
	},
	unknown_delivery_site: null,
	delivery_site_country: {
		name: "France",
		name_en: "France",
		code_pays: "FR",
	},
	delivery_type: "UNKNOWN",
	lot_status: "PENDING",
	correction_status: "NO_PROBLEMO",
	audit_status: "UNKNOWN",
	volume: 50000,
	weight: 38900,
	lhv_amount: 1050000,
	feedstock: {
		name: "Blé",
		name_en: "Wheat",
		code: "BLE",
		category: "CONV",
		is_double_compte: false,
	},
	biofuel: {
		name: "Éthanol",
		name_en: "Ethanol",
		code: "ETH",
	},
	country_of_origin: {
		name: "République tchèque",
		name_en: "Czech Republic",
		code_pays: "CZ",
	},
	eec: 14.5,
	el: 0,
	ep: 7,
	etd: 2,
	eu: 0,
	esca: 0,
	eccs: 0,
	eccr: 0,
	eee: 0,
	ghg_total: 23.5,
	ghg_reference: 83.8,
	ghg_reduction: 71.96,
	ghg_reference_red_ii: 94,
	ghg_reduction_red_ii: 75,
	free_field: "MT AC-D ",
	added_by: {
		id: 90,
		name: "Cargill International Sa",
		entity_type: "Trader",
		has_mac: false,
		has_trading: true,
		has_direct_deliveries: true,
		has_stocks: true,
		preferred_unit: "l",
		legal_name: "",
		registration_id: "",
		sustainability_officer_phone_number: "",
		sustainability_officer: "",
		registered_address: "",
	},
	created_at: "2022-08-19T18:00:01.470345+02:00",
	highlighted_by_auditor: false,
	highlighted_by_admin: false,
	carbure_vendor: null,
	vendor_certificate: null,
	vendor_certificate_type: "",
	data_reliability_score: "E",
}

export const lots = [lot, lot, lot]

const lotError: LotError = {
	error: "NOT_GOOD_VALUE",
	is_blocking: true,
	field: "biofuel",
	fields: null,
	value: null,
	extra: null,
	acked_by_creator: false,
	acked_by_recipient: false,
	acked_by_admin: false,
	acked_by_auditor: false,
}
const lotUpdateError1 = [lotError, lotError]
const lotUpdateError2 = [lotError]
export const lotsUpdateErrorsResponse: LotsUpdateResponse = {
	errors: { 287367: lotUpdateError1, 287368: lotUpdateError2 },
}
