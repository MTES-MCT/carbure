import {
  PathsApiElecV2ProvisionCertificatesGetParametersQueryOrder_by,
  SourceEnum,
} from "api-schema"
import { CBQueryParams } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"

export { SourceEnum as ProvisionCertificateSource }

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
