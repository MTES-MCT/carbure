import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputMaterialUnit,
} from "../../types"
import Tag from "@codegouvfr/react-dsfr/Tag"
import {
  convertSupplyPlanInputVolume,
  getSupplyPlanInputSource,
} from "../../utils"
import { getDepartmentName } from "common/utils/geography"
import { formatNumber } from "common/utils/formatters"

export const useSupplyPlanColumns = () => {
  const { t } = useTranslation()

  const columns: Column<BiomethaneSupplyInput>[] = [
    {
      header: t("Provenance"),
      cell: (input) => <Tag>{getSupplyPlanInputSource(input.source)}</Tag>,
    },
    {
      header: t("Intrant"),
      cell: (input) => <Cell text={input.input_name?.name} />,
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
                input.dry_matter_ratio_percent ?? 0
              )
            : input.volume
        return <Cell text={`${formatNumber(volume)} tMB`} />
      },
    },
  ]

  return columns
}
