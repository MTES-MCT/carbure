import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiBiomethaneSupplyInputGetParametersQuerySource as BiomethaneSupplyInputSource,
  PathsApiBiomethaneSupplyInputGetParametersQueryCategory as BiomethaneSupplyInputCategory,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"

export type BiomethaneSupplyInput = apiTypes["BiomethaneSupplyInput"]

export type BiomethaneSupplyInputQueryBuilder = QueryBuilder<never, never>
export type BiomethaneSupplyInputQuery =
  BiomethaneSupplyInputQueryBuilder["query"]
enum BiomethaneSupplyInputFilter {
  source = "source",
  category = "category",
  type = "type",
}
export {
  BiomethaneSupplyInputSource,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputCategory,
}
