import {
  PathsApiElecProvisionCertificatesQualichargeFiltersGetParametersQueryFilter as QualichargeFilter,
  PathsApiElecProvisionCertificatesQualichargeGetParametersQueryValidated_by as QualichargeValidatedBy,
} from "api-schema"
import {
  QueryConfig,
  QueryParams as QueryParams2,
} from "common/hooks/new-query-builder"
import { CBQueryParams } from "common/hooks/query-builder-2"
import { apiTypes, QueryParams } from "common/services/api-fetch.types"

export { QualichargeValidatedBy, QualichargeFilter }

export type ElecDataQualichargeOverview =
  apiTypes["ElecProvisionCertificateQualicharge"]

export enum QualichargeTab {
  PENDING = "pending",
  VALIDATED = "validated",
}

export type QualichargeQuery = CBQueryParams<
  string[],
  QualichargeTab,
  unknown
> &
  Pick<
    QueryParams<"/elec/provision-certificates-qualicharge/">,
    "validated_by" | "date_from" | "operating_unit"
  >

export type QualichargeQueryConfig2 = QueryConfig<QualichargeTab>
export type QualichargeQuery2 = QueryParams2<QualichargeQueryConfig2> &
  Pick<
    QueryParams<"/elec/provision-certificates-qualicharge/">,
    "validated_by" | "date_from" | "operating_unit"
  >
