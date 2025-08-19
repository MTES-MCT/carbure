import {
  PathsApiElecProvisionCertificatesQualichargeFiltersGetParametersQueryFilter as QualichargeFilter,
  PathsApiElecProvisionCertificatesQualichargeGetParametersQueryValidated_by as QualichargeValidatedBy,
} from "api-schema"
import { QueryBuilder } from "common/hooks/new-query-builder"
import { apiTypes, QueryParams } from "common/services/api-fetch.types"

export { QualichargeValidatedBy, QualichargeFilter }

export type ElecDataQualichargeOverview =
  apiTypes["ElecProvisionCertificateQualicharge"]

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
