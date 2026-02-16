import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputQuery,
  BiomethaneSupplyInputQueryBuilder,
  BiomethaneSupplyInputSource,
} from "./types"
import { getSupplyPlanInputSource } from "./utils"
import { getSupplyPlanInputFilters, getSupplyPlanInputs } from "./api"
import { defaultNormalizer } from "common/utils/normalize"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { useQuery } from "common/hooks/async"

export const useGetFilterOptions = (query: BiomethaneSupplyInputQuery) => {
  const { t } = useTranslation()
  const { selectedEntityId } = useSelectedEntity()

  const filterLabels = {
    [BiomethaneSupplyInputFilter.source]: t("Provenance"),
    [BiomethaneSupplyInputFilter.input_name]: t("Intrant"),
  }

  const normalizers = {
    [BiomethaneSupplyInputFilter.source]: (value: string) => ({
      value,
      label: getSupplyPlanInputSource(value as BiomethaneSupplyInputSource),
    }),
    [BiomethaneSupplyInputFilter.input_name]: (value: string) =>
      defaultNormalizer(value),
  }

  return {
    normalizers,
    filterLabels,
    getFilterOptions: (filter: BiomethaneSupplyInputFilter) =>
      getSupplyPlanInputFilters(query, filter, selectedEntityId),
  }
}

export const useSupplyPlanQuery = (year: number) => {
  const { selectedEntityId } = useSelectedEntity()
  const { state, actions, query } = useQueryBuilder<
    BiomethaneSupplyInputQueryBuilder["config"]
  >({
    year,
  })

  const { getFilterOptions, filterLabels, normalizers } =
    useGetFilterOptions(query)

  const { result: supplyInputs, loading } = useQuery(getSupplyPlanInputs, {
    key: `supply-plan-inputs`,
    params: [query, selectedEntityId],
  })

  return {
    queryBuilder: { state, actions, query },
    filterOptions: { getFilterOptions, filterLabels, normalizers },
    supplyPlan: { supplyInputs, loading },
  }
}
