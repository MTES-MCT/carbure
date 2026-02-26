import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputMaterialUnit,
  BiomethaneSupplyInputQuery,
} from "./types"
import Tag from "@codegouvfr/react-dsfr/Tag"
import { convertSupplyPlanInputVolume } from "./utils"
import { getDepartmentName } from "common/utils/geography"
import { getSupplyPlanInputFilters } from "./api"
import { defaultNormalizer } from "common/utils/normalize"
import { formatNumber } from "common/utils/formatters"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const useSupplyPlanColumns = () => {
  const { t } = useTranslation()

  const columns: Column<BiomethaneSupplyInput>[] = [
    {
      header: t("Intrant"),
      cell: (input) => <Cell text={input.feedstock?.name} />,
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
        if (!input.volume) return <Cell text={t("N/A")} />

        const volume =
          input.material_unit === BiomethaneSupplyInputMaterialUnit.DRY
            ? convertSupplyPlanInputVolume(
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
  const { selectedEntityId } = useSelectedEntity()

  const filterLabels = {
    [BiomethaneSupplyInputFilter.feedstock]: t("Intrant"),
  }

  const normalizers = {
    [BiomethaneSupplyInputFilter.feedstock]: (value: string) =>
      defaultNormalizer(value),
  }

  return {
    normalizers,
    filterLabels,
    getFilterOptions: (filter: BiomethaneSupplyInputFilter) =>
      getSupplyPlanInputFilters(query, filter, selectedEntityId),
  }
}
