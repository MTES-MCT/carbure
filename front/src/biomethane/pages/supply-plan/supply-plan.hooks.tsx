import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputCategory,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputQuery,
  BiomethaneSupplyInputSource,
} from "./types"
import Tag from "@codegouvfr/react-dsfr/Tag"
import { getSupplyPlanInputCategory, getSupplyPlanInputSource } from "./utils"
import { getDepartmentName } from "common/utils/geography"
import { getSupplyPlanInputFilters } from "./api"
import { defaultNormalizer } from "common/utils/normalize"

export const useSupplyPlanColumns = () => {
  const { t } = useTranslation()

  const columns: Column<BiomethaneSupplyInput>[] = [
    {
      header: t("Provenance"),
      cell: (input) => <Tag>{getSupplyPlanInputSource(input.source)}</Tag>,
    },
    {
      header: t("Catégorie"),
      cell: (input) => <Cell text={input.input_category} />,
    },
    {
      header: t("Intrant"),
      cell: (input) => <Cell text={input.input_type} />,
    },
    {
      header: t("Département"),
      cell: (input) =>
        input.origin_department && (
          <Tag>{`${input.origin_department} - ${getDepartmentName(input.origin_department) ?? ""}`}</Tag>
        ),
    },
    {
      header: t("Volume (t)"),
      cell: (input) => <Cell text={input.volume} />,
    },
  ]

  return columns
}

export const useGetFilterOptions = (query: BiomethaneSupplyInputQuery) => {
  const { t } = useTranslation()

  const filterLabels = {
    [BiomethaneSupplyInputFilter.source]: t("Provenance"),
    [BiomethaneSupplyInputFilter.category]: t("Catégorie"),
    [BiomethaneSupplyInputFilter.type]: t("Intrant"),
  }

  const normalizers = {
    [BiomethaneSupplyInputFilter.source]: (value: string) => ({
      value,
      label: getSupplyPlanInputSource(value as BiomethaneSupplyInputSource),
    }),
    [BiomethaneSupplyInputFilter.category]: (value: string) => ({
      value,
      label: getSupplyPlanInputCategory(value as BiomethaneSupplyInputCategory),
    }),
    [BiomethaneSupplyInputFilter.type]: (value: string) =>
      defaultNormalizer(value),
  }

  return {
    normalizers,
    filterLabels,
    getFilterOptions: (filter: BiomethaneSupplyInputFilter) =>
      getSupplyPlanInputFilters(query, filter),
  }
}
