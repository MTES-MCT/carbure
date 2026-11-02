import { apiTypes } from "common/services/api-fetch.types"
import { QueryBuilder } from "common/hooks/query-builder-2"

export type BiomethaneProviderDeclaration =
  apiTypes["BiomethaneProviderDeclaration"]

export type BiomethaneProviderDeclarationsQueryBuilder = QueryBuilder<
  never,
  never
>
export type BiomethaneProviderDeclarationsQuery =
  BiomethaneProviderDeclarationsQueryBuilder["query"]
