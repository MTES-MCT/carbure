import { useTranslation } from "react-i18next"
import { Column } from "common/components/table2"
import { BiomethaneEnergyMonthlyReportDataRequest } from "../../types"
import { formatMonth } from "common/utils/formatters"
import { NumberInput } from "common/components/inputs2"

export type BiomethaneEnergyMonthlyReportForm = Partial<
  Exclude<BiomethaneEnergyMonthlyReportDataRequest, "month">
> & {
  month: number
}

export const useDeclareMonthlyQuantityColumns = ({
  isReadOnly,
  updateCellValue,
}: {
  isReadOnly: boolean
  updateCellValue: (
    month: number,
    field: keyof BiomethaneEnergyMonthlyReportForm,
    value: number | undefined
  ) => void
}) => {
  const { t } = useTranslation()

  const columns: Column<BiomethaneEnergyMonthlyReportForm>[] = [
    {
      header: t("Mois"),
      cell: (item) => formatMonth(item.month),
      style: {
        maxWidth: "145px",
      },
    },
    {
      header: t("Volume injecté (Nm³)"),
      cell: (item) => (
        <NumberInput
          value={item.injected_volume_nm3}
          onChange={(value) =>
            updateCellValue(item.month, "injected_volume_nm3", value)
          }
          readOnly={isReadOnly}
          required
        />
      ),
    },
    {
      header: t("Débit moyen mensuel (Nm³/h)"),
      cell: (item) => (
        <NumberInput
          value={item.average_monthly_flow_nm3_per_hour}
          onChange={(value) =>
            updateCellValue(
              item.month,
              "average_monthly_flow_nm3_per_hour",
              value
            )
          }
          readOnly={isReadOnly}
          required
        />
      ),
    },
    {
      header: t("Heures d'injection (h)"),
      cell: (item) => (
        <NumberInput
          value={item.injection_hours}
          onChange={(value) =>
            updateCellValue(item.month, "injection_hours", value)
          }
          readOnly={isReadOnly}
          required
        />
      ),
    },
  ]

  return columns
}
