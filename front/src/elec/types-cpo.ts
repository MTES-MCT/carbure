import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import {
	ElecProvisionCertificatePreview,
	ElecTransferCertificate,
	ElecTransferCertificateFilter,
	ElecTransferCertificatePreview,
} from "./types"
import { ElecOperatorSnapshot, ElecOperatorStatus } from "./types-operator"

export interface ElecCPOSnapshot {
	provisioned_energy: number
	remaining_energy: number
	provision_certificates_available: number
	provision_certificates_history: number
	transferred_energy: number
	transfer_certificates_pending: number
	transfer_certificates_accepted: number
	transfer_certificates_rejected: number
}

export enum ElecCPOProvisionCertificateStatus {
	Available = "AVAILABLE",
	History = "HISTORY",
}

export type ElecCPOProvisionCertificateFilterSelection = Partial<
	Record<ElecCPOProvisionCertificateFilter, string[]>
>

export interface ElecCPOProvisionCertificateStates {
	entity: Entity
	year: number
	status: ElecCPOProvisionCertificateStatus
	filters: ElecCPOProvisionCertificateFilterSelection
	search?: string
	selection: number[]
	page: number
	limit?: number
	order?: Order
	snapshot?: ElecCPOSnapshot
}

export enum ElecCPOProvisionCertificateFilter {
	Quarter = "quarter",
	OperatingUnit = "operating_unit",
}

export interface ElecCPOProvisionCertificateQuery {
	entity_id: number
	status?: string
	year?: number
	search?: string
	sort_by?: string
	order?: string
	from_idx?: number
	limit?: number
	[ElecCPOProvisionCertificateFilter.OperatingUnit]?: string[]
	[ElecCPOProvisionCertificateFilter.Quarter]?: string[]
}

export interface ElecProvisionCertificatesData {
	elec_provision_certificates: ElecProvisionCertificatePreview[]
	from: number
	ids: number[]
	returned: number
	total: number
}
export interface ElecTransferCertificatesData {
	elec_transfer_certificates: ElecTransferCertificatePreview[]
	from: number
	ids: number[]
	returned: number
	total: number
}

export enum ElecTransferCertificateStatus {
	Pending = "PENDING",
	Accepted = "ACCEPTED",
	Rejected = "REJECTED",
}

export type ElecTransferCertificateFilterSelection = Partial<
	Record<ElecTransferCertificateFilter, string[]>
>

export interface ElecTransferCertificateStates {
	entity: Entity
	year: number
	status: ElecTransferCertificateStatus | ElecOperatorStatus
	filters: ElecTransferCertificateFilterSelection
	search?: string
	selection: number[]
	page: number
	limit?: number
	order?: Order
	snapshot?: ElecCPOSnapshot | ElecOperatorSnapshot
}

export interface ElecTransferCertificateQuery {
	entity_id: number
	status?: string
	year?: number
	search?: string
	sort_by?: string
	order?: string
	from_idx?: number
	limit?: number
	// [ElecCPOTransferCertificateFilter.CertificateId]?: string[]
	// [ElecTransferCertificateFilter.CertificateId]?: string[]
}
