import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiBiomethaneSupplyInputGetParametersQuerySource as BiomethaneSupplyInputSource,
  PathsApiBiomethaneSupplyInputGetParametersQueryCategory as BiomethaneSupplyInputCategory,
  PathsApiBiomethaneSupplyInputFiltersGetParametersQueryFilter as BiomethaneSupplyInputFilter,
  CropTypeEnum as BiomethaneSupplyInputCropType,
  MaterialUnitEnum as BiomethaneSupplyInputMaterialUnit,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"

export type BiomethaneSupplyInput = apiTypes["BiomethaneSupplyInput"]

export type BiomethaneSupplyInputQueryBuilder = QueryBuilder<never, never>
export type BiomethaneSupplyInputQuery =
  BiomethaneSupplyInputQueryBuilder["query"]

export type BiomethaneSupplyInputForm = apiTypes["BiomethaneSupplyInputCreate"]

export {
  BiomethaneSupplyInputSource,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputCategory,
  BiomethaneSupplyInputCropType,
  BiomethaneSupplyInputMaterialUnit,
}
