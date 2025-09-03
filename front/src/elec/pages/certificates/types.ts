import {
  PathsApiElecProvisionCertificatesGetParametersQueryOrder_by,
  PathsApiElecTransferCertificatesGetParametersQueryOrder_by,
  PathsApiSafTicketsGetParametersQueryStatus as TransferCertificateStatus,
  PathsApiElecProvisionCertificatesGetParametersQuerySource,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"

export { PathsApiElecProvisionCertificatesGetParametersQuerySource as ProvisionCertificateSource }
export { TransferCertificateStatus }

export type ElecCertificateSnapshot = {
  provision_certificates_available: number
  provision_certificates_history: number
  transfer_certificates_pending: number
  transfer_certificates_accepted: number
  transfer_certificates_rejected: number
}

export type ProvisionCertificateStatus = "available" | "history"

export enum ProvisionCertificateFilter {
  Quarter = "quarter",
  OperatingUnit = "operating_unit",
  Source = "source",
  Cpo = "cpo",
}

export type ProvisionCertificateOrder =
  PathsApiElecProvisionCertificatesGetParametersQueryOrder_by

export type ProvisionCertificatesQueryBuilder = QueryBuilder<
  ProvisionCertificateStatus,
  ProvisionCertificateOrder[]
>
export type ProvisionCertificatesQuery =
  ProvisionCertificatesQueryBuilder["query"]

export type ProvisionCertificate = apiTypes["ElecProvisionCertificate"]

export enum TransferCertificateFilter {
  Month = "month",
  Operator = "operator",
  Cpo = "cpo",
  UsedInTiruert = "used_in_tiruert",
}

export type TransferCertificateOrder =
  PathsApiElecTransferCertificatesGetParametersQueryOrder_by

export type TransferCertificatesQueryBuilder = QueryBuilder<
  TransferCertificateStatus,
  TransferCertificateOrder[]
>
export type TransferCertificatesQuery =
  TransferCertificatesQueryBuilder["query"]

export type TransferCertificate = apiTypes["ElecTransferCertificate"]
