import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputCategory,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputMaterialUnit,
  BiomethaneSupplyInputQuery,
  BiomethaneSupplyInputSource,
} from "./types"
import Tag from "@codegouvfr/react-dsfr/Tag"
import {
  convertSupplyPlanInputVolume,
  getSupplyPlanInputCategory,
  getSupplyPlanInputSource,
} from "./utils"
import { getDepartmentName } from "common/utils/geography"
import { getSupplyPlanInputFilters } from "./api"
import { defaultNormalizer } from "common/utils/normalize"
import { formatNumber } from "common/utils/formatters"

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
      header: t("Tonnage (tMB)"),
      cell: (input) => {
        const volume =
          input.material_unit === BiomethaneSupplyInputMaterialUnit.DRY
            ? convertSupplyPlanInputVolume(
                input.volume,
                input.volume,
                input.dry_matter_ratio_percent ?? 0
              )
            : input.volume
        return <Cell text={`${formatNumber(volume)} tMB`} />
      },
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
