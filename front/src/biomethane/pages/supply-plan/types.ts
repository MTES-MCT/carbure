import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiBiomethaneSupplyInputFiltersGetParametersQueryFilter as BiomethaneSupplyInputFilter,
  MaterialUnitEnum as BiomethaneSupplyInputMaterialUnit,
  TypeCiveEnum as BiomethaneSupplyInputTypeCive,
  CollectionTypeEnum as BiomethaneSupplyInputCollectionType,
  BiomethaneSupplyInputSourceEnum as BiomethaneSupplyInputSource,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"

export type BiomethaneSupplyInput = apiTypes["BiomethaneSupplyInput"]

export type BiomethaneSupplyInputQueryBuilder = QueryBuilder<never, never>
export type BiomethaneSupplyInputQuery =
  BiomethaneSupplyInputQueryBuilder["query"]

export type BiomethaneSupplyInputForm = apiTypes["BiomethaneSupplyInputCreate"]

export {
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputMaterialUnit,
  BiomethaneSupplyInputTypeCive,
  BiomethaneSupplyInputCollectionType,
  BiomethaneSupplyInputSource,
}
