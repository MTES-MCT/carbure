import { CBQueryParams } from "common/hooks/query-builder-2"
import {
  PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by as AgreementOrder,
  PathsApiDoubleCountingApplicationsFiltersGetParametersQueryOrder_by as ApplicationOrder,
} from "api-schema"

export { AgreementOrder, ApplicationOrder }

export type AgreementListQuery = CBQueryParams<
  AgreementOrder[],
  string,
  undefined
>

export type AgreementFilterSelection = Partial<
  Record<AgreementFilter, string[]>
>

export enum AgreementFilter {
  Certificate_id = "certificate_id",
  Producers = "producers",
  ProductionSites = "production_sites",
}

export type ApplicationListQuery = CBQueryParams<
  ApplicationOrder[],
  string,
  undefined
>
