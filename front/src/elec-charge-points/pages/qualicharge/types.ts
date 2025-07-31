import {
  PathsApiElecProvisionCertificatesQualichargeFiltersGetParametersQueryFilter as QualichargeFilter,
  PathsApiElecProvisionCertificatesQualichargeGetParametersQueryValidated_by as QualichargeValidatedBy,
} from "api-schema"
import { CBQueryParams } from "common/hooks/query-builder-2"
import { apiTypes, QueryParams } from "common/services/api-fetch.types"

export { QualichargeFilter, QualichargeValidatedBy }

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
