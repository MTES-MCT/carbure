import { useGetFilterOptions } from "biomethane/pages/supply-plan/supply-plan.hooks"
import {
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputQuery,
} from "biomethane/pages/supply-plan/types"
import { defaultNormalizer } from "common/utils/normalize"
import { useTranslation } from "react-i18next"

export const useGetFiltersOptionsAdmin = (
  query: BiomethaneSupplyInputQuery
) => {
  const { t } = useTranslation()
  const {
    getFilterOptions,
    filterLabels: filterLabelsSupplyPlan,
    normalizers: normalizersSupplyPlan,
  } = useGetFilterOptions(query)

  const filterLabels = {
    [BiomethaneSupplyInputFilter.producer_name]: t("Producteur"),
  }

  const normalizers = {
    [BiomethaneSupplyInputFilter.producer_name]: (value: string) =>
      defaultNormalizer(value),
  }

  return {
    filterLabels: {
      ...filterLabels,
      ...filterLabelsSupplyPlan,
    },
    normalizers: {
      ...normalizersSupplyPlan,
      ...normalizers,
    },
    getFilterOptions,
  }
}
