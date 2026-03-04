import { useSupplyPlanColumns } from "biomethane/pages/supply-plan/components/supply-plan-table/supply-plan-table.hooks"
import { useGetFilterOptions } from "biomethane/pages/supply-plan/supply-plan.hooks"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputQuery,
} from "biomethane/pages/supply-plan/types"
import { Cell, Column } from "common/components/table2"
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

export const useSupplyInputsColumnsAdmin = () => {
  const { t } = useTranslation()
  const _columns = useSupplyPlanColumns()

  const columns: Column<BiomethaneSupplyInput>[] = [
    {
      header: t("Producteur"),
      cell: (input) => <Cell text={input.producer?.name} />,
    },
  ]

  return [...columns, ..._columns]
}
