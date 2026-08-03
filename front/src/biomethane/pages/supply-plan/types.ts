import { apiTypes } from "common/services/api-fetch.types"
import { QueryBuilder } from "common/hooks/query-builder-2"

export type BiomethaneSupplyInput = apiTypes["BiomethaneSupplyInput"]
export type BiomethaneSupplyInputResponse =
  apiTypes["PaginatedBiomethaneSupplyInputList"]
export type BiomethaneSupplyInputQueryBuilder = QueryBuilder<never, never>
export type BiomethaneSupplyInputQuery =
  BiomethaneSupplyInputQueryBuilder["query"]

export type BiomethaneSupplyInputForm = apiTypes["BiomethaneSupplyInputCreate"]

export type TariffCoefficients = apiTypes["TariffCoefficients"]
export type TariffCoefficientProportions =
  apiTypes["TariffCoefficientProportions"]

export {
  PathsApiBiomethaneSupplyInputFiltersGetParametersQueryFilter as BiomethaneSupplyInputFilter,
  MaterialUnitEnum as BiomethaneSupplyInputMaterialUnit,
  TypeCiveEnum as BiomethaneSupplyInputTypeCive,
  CollectionTypeEnum as BiomethaneSupplyInputCollectionType,
  PathsApiBiomethaneSupplyInputGetParametersQuerySource as BiomethaneSupplyInputSource,
  CropTypeEnum as CropType,
} from "api-schema"
