import { Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { BiomethaneDigestateSpreading } from "../../types"
import { getDepartmentName } from "common/utils/geography"

export const useSpreadingColumns = () => {
  const { t } = useTranslation()

  const columns: Column<BiomethaneDigestateSpreading>[] = [
    {
      key: "department",
      header: t("Département"),
      cell: (spreadingData) =>
        getDepartmentName(spreadingData.spreading_department),
    },
    {
      key: "surface",
      header: t("Quantité épandue (t)"),
      cell: (spreadingData) => spreadingData.spread_quantity,
    },
    {
      key: "surface",
      header: t("Superficie des parcelles épandues (ha)"),
      cell: (spreadingData) => spreadingData.spread_parcels_area,
    },
  ]

  return columns
}
