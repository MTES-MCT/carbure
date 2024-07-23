import {
	biocarburant,
	country,
	deliverySite,
	matierePremiere,
	operator,
	producer,
	productionSite,
} from "carbure/__test__/data"
import { clone } from "carbure/__test__/helpers"
import { LotDetails } from "transaction-details/types"
import {
	CorrectionStatus,
	DeliveryType,
	Lot,
	LotError,
	LotStatus,
} from "transactions/types"

export const lot: Lot = {
	id: 0,
	lot_status: LotStatus.Draft,
	correction_status: CorrectionStatus.NoProblem,
	delivery_type: DeliveryType.Unknown,
	year: 2020,
	period: 202001,
	carbure_id: "TEST01",
	carbure_producer: producer,
	unknown_producer: "",
	carbure_production_site: productionSite,
	production_site_certificate: "2BS - KNOWN PSITE",
	unknown_production_site: "",
	production_country: country,
	production_site_commissioning_date: "2000-01-31",
	production_site_double_counting_certificate: "",
	volume: 12345,
	weight: 12345,
	lhv_amount: 1245,
	feedstock: matierePremiere,
	biofuel: biocarburant,
	country_of_origin: country,
	eec: 12,
	el: 0,
	ep: 0,
	etd: 0,
	eu: 0,
	esca: 1,
	eccs: 0,
	eccr: 0,
	eee: 0,
	ghg_total: 11,
	ghg_reference: 83.8,
	ghg_reduction: 86.87,
	ghg_reference_red_ii: 94,
	ghg_reduction_red_ii: 84.23124,
	added_by: producer,
	carbure_supplier: producer,
	unknown_supplier: null,
	supplier_certificate: "ISCC2000 - Supplier",
	transport_document_reference: "DAETEST",
	carbure_client: operator,
	unknown_client: "",
	delivery_date: "2020-01-31",
	carbure_delivery_site: deliverySite,
	unknown_delivery_site: "",
	delivery_site_country: country,
	free_field: "",
	created_at: "2020-01-31",
}

export const lotDetails: LotDetails = {
	lot: lot,
	comments: [],
	errors: [],
	updates: [],
	distance: null,
	parent_lot: null,
	parent_stock: null,
	has_parent_stock: null,
	children_lot: [],
	children_stock: [],
	certificates: {
		production_site_certificate: null,
		production_site_double_counting_certificate: null,
		supplier_certificate: null,
		vendor_certificate: null,
	},
	score: [],
	is_read_only: false,
	disabled_fields: [],
}

export const errors: LotError[] = [
	{
		error: "UNKNOWN_PRODUCTION_SITE",
		is_blocking: true,
		field: "carbure_production_site",
		value: null,
		extra: null,
		fields: null,
		acked_by_creator: false,
		acked_by_recipient: false,
		acked_by_admin: false,
		acked_by_auditor: false,
	},
	{
		error: "MISSING_PRODUCTION_SITE_COMDATE",
		is_blocking: true,
		field: "production_site_commissioning_date",
		value: null,
		extra: null,
		fields: null,
		acked_by_creator: false,
		acked_by_recipient: false,
		acked_by_admin: false,
		acked_by_auditor: false,
	},
	{
		error: "NO_PRODSITE_CERT",
		is_blocking: false,
		field: "production_site_certificate",
		value: null,
		extra: null,
		fields: null,
		acked_by_creator: false,
		acked_by_recipient: false,
		acked_by_admin: false,
		acked_by_auditor: false,
	},
]

export const errorDetails: LotDetails = {
	...clone(lotDetails),
	errors: errors,
}

export const tofixDetails: LotDetails = {
	...clone(lotDetails),
	lot: {
		...lot,
		lot_status: LotStatus.Pending,
		correction_status: CorrectionStatus.InCorrection,
	},
	comments: [
		{
			entity: operator,
			user: "operator@test.com",
			comment_type: "REGULAR",
			comment_dt: "2021-11-30T14:02:45.832791+01:00",
			comment: "Ces lots ont été affectés par erreur",
		},
	],
}

export const rejectedDetails: LotDetails = {
	...clone(lotDetails),
	lot: {
		...lot,
		lot_status: LotStatus.Rejected,
		correction_status: CorrectionStatus.NoProblem,
	},
	comments: [
		{
			entity: operator,
			user: "operator@test.com",
			comment_type: "REGULAR",
			comment_dt: "2021-11-30T14:02:45.832791+01:00",
			comment: "Ces lots ont été affectés par erreur",
		},
	],
}

export const sentDetails: LotDetails = {
	...clone(lotDetails),
	lot: {
		...lot,
		lot_status: LotStatus.Pending,
		correction_status: CorrectionStatus.NoProblem,
	},
}
