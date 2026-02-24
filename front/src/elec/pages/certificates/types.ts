import {
  PathsApiElecProvisionCertificatesGetParametersQueryOrder_by,
  PathsApiElecTransferCertificatesGetParametersQueryOrder_by,
  PathsApiSafTicketsGetParametersQueryStatus as TransferCertificateStatus,
  PathsApiElecProvisionCertificatesGetParametersQuerySource,
  PathsApiElecProvisionCertificatesFiltersGetParametersQueryFilter as ProvisionCertificateFilter,
  PathsApiElecTransferCertificatesFiltersGetParametersQueryFilter as TransferCertificateFilter,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"

export { PathsApiElecProvisionCertificatesGetParametersQuerySource as ProvisionCertificateSource }
export {
  TransferCertificateStatus,
  TransferCertificateFilter,
  ProvisionCertificateFilter,
}

export type ElecCertificateSnapshot = {
  provision_certificates: number
  transfer_certificates_pending: number
  transfer_certificates_accepted: number
  transfer_certificates_rejected: number
}

export type ProvisionCertificateStatus = "history"

export type ProvisionCertificateOrder =
  PathsApiElecProvisionCertificatesGetParametersQueryOrder_by

export type ProvisionCertificatesQueryBuilder = QueryBuilder<
  ProvisionCertificateStatus,
  ProvisionCertificateOrder[]
>
export type ProvisionCertificatesQuery =
  ProvisionCertificatesQueryBuilder["query"]

export type ProvisionCertificate = apiTypes["ElecProvisionCertificate"]

export type TransferCertificateOrder =
  PathsApiElecTransferCertificatesGetParametersQueryOrder_by

export type TransferCertificatesQueryBuilder = QueryBuilder<
  TransferCertificateStatus,
  TransferCertificateOrder[]
>
export type TransferCertificatesQuery =
  TransferCertificatesQueryBuilder["query"]

export type TransferCertificate = apiTypes["ElecTransferCertificate"]
