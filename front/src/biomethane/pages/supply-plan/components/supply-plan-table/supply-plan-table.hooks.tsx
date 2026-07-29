import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { BiomethaneSupplyInput } from "../../types"
import Tag from "@codegouvfr/react-dsfr/Tag"
import { getSupplyPlanInputSource } from "../../utils"
import { getDepartmentName } from "common/utils/geography"
import { formatNumber } from "common/utils/formatters"

export const useSupplyPlanColumns = () => {
  const { t } = useTranslation()

  const columns: Column<BiomethaneSupplyInput>[] = [
    {
      header: t("Provenance"),
      cell: (input) =>
        input.source ? (
          <Tag>{getSupplyPlanInputSource(input.source)}</Tag>
        ) : (
          "-"
        ),
    },
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
        if (input.volume_tmb == null) return <Cell text={t("N/A")} />
        return <Cell text={`${formatNumber(input.volume_tmb)} tMB`} />
      },
    },
  ]

  return columns
}
