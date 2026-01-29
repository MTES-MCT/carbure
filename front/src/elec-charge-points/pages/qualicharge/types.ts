import {
  PathsApiElecProvisionCertificatesQualichargeFiltersGetParametersQueryFilter as QualichargeFilter,
  PathsApiElecProvisionCertificatesQualichargeGetParametersQueryValidated_by as QualichargeValidatedBy,
  PathsApiElecProvisionCertificatesQualichargeGetParametersQueryGroup_by as QualichargeGroupBy,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"
import { apiTypes, QueryParams } from "common/services/api-fetch.types"

export { QualichargeValidatedBy, QualichargeFilter, QualichargeGroupBy }

export type ElecDataQualichargeOverview =
  apiTypes["ElecProvisionCertificateQualicharge"]

export type ElecDataQualichargeGroupedByOperatingUnit =
  apiTypes["ElecProvisionCertificateQualichargeGrouped"]

export enum QualichargeTab {
  PENDING = "pending",
  VALIDATED = "validated",
}

// export type QualichargeQuery = CBQueryParams<
//   string[],
//   QualichargeTab,
//   unknown
// > &
//   Pick<
//     QueryParams<"/elec/provision-certificates-qualicharge/">,
//     "validated_by" | "date_from" | "operating_unit"
//   >

export type QualichargeQueryBuilder = QueryBuilder<QualichargeTab>

export type QualichargeQuery = QualichargeQueryBuilder["query"] &
  Pick<
    QueryParams<"/elec/provision-certificates-qualicharge/">,
    "validated_by" | "date_from" | "operating_unit"
  >
