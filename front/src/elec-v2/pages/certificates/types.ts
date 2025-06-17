import {
  PathsApiElecV2ProvisionCertificatesGetParametersQueryOrder_by,
  PathsApiElecV2TransferCertificatesGetParametersQueryOrder_by,
  PathsApiSafTicketsGetParametersQueryStatus,
  SourceEnum,
} from "api-schema"
import { CBQueryParams } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"

export { SourceEnum as ProvisionCertificateSource }
export { PathsApiSafTicketsGetParametersQueryStatus as TransferCertificateStatus }

export type ProvisionCertificateStatus = "available" | "history"

export enum ProvisionCertificateFilter {
  Quarter = "quarter",
  OperatingUnit = "operating_unit",
  Source = "source",
  Cpo = "cpo",
}

export type ProvisionCertificateOrder =
  PathsApiElecV2ProvisionCertificatesGetParametersQueryOrder_by

export type ProvisionCertificatesQuery = CBQueryParams<
  ProvisionCertificateOrder[],
  ProvisionCertificateStatus,
  undefined
>

export type ProvisionCertificate = apiTypes["ElecProvisionCertificate"]

export enum TransferCertificateFilter {
  Operator = "operator",
  Cpo = "cpo",
}

export type TransferCertificateOrder =
  PathsApiElecV2TransferCertificatesGetParametersQueryOrder_by

export type TransferCertificatesQuery = CBQueryParams<
  TransferCertificateOrder[],
  PathsApiSafTicketsGetParametersQueryStatus,
  undefined
>

export type TransferCertificate = apiTypes["ElecTransferCertificate"]
