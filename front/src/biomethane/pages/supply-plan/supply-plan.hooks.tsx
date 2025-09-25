import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputQuery,
} from "./types"
import Tag from "@codegouvfr/react-dsfr/Tag"
import { getSupplyPlanInputSource } from "./utils"
import { getDepartmentName } from "common/utils/geography"
import { getSupplyPlanInputFilters } from "./api"

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
      cell: (input) => (
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

  const getFilterOptions = async (filter: string) => {
    const data = await getSupplyPlanInputFilters(
      query,
      filter as BiomethaneSupplyInputFilter
    )

    return data
  }

  const filterLabels = {
    [BiomethaneSupplyInputFilter.source]: t("Provenance"),
    [BiomethaneSupplyInputFilter.category]: t("Catégorie"),
    [BiomethaneSupplyInputFilter.type]: t("Intrant"),
  }

  return { getFilterOptions, filterLabels }
}
