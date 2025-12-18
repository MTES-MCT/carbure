import {
  PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by as AgreementOrder,
  PathsApiDoubleCountingApplicationsFiltersGetParametersQueryOrder_by as ApplicationOrder,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"

export { AgreementOrder, ApplicationOrder }

export type AgreementListQueryBuilder = QueryBuilder<string, AgreementOrder[]>
export type AgreementListQuery = AgreementListQueryBuilder["query"]

export type AgreementFilterSelection = Partial<
  Record<AgreementFilter, string[]>
>

export enum AgreementFilter {
  Certificate_id = "certificate_id",
  Producers = "producers",
  ProductionSites = "production_sites",
  Status = "status_values",
}

export type ApplicationListQueryBuilder = QueryBuilder<
  string,
  ApplicationOrder[]
>
export type ApplicationListQuery = ApplicationListQueryBuilder["query"]
