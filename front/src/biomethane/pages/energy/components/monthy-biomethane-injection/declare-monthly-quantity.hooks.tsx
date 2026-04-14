import { useTranslation } from "react-i18next"
import { Column } from "common/components/table2"
import { BiomethaneEnergyMonthlyReportDataRequest } from "../../types"
import { formatMonth, formatNumber } from "common/utils/formatters"
import { NumberInput, TextInput } from "common/components/inputs2"
import {
  getHoursInMonth,
  getInjectionHours,
  isInjectionHoursInError,
} from "./declare-monthly-quantity.utils"
import { useAnnualDeclarationYear } from "biomethane/providers/annual-declaration"

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
  const selectedYear = useAnnualDeclarationYear()

  if (!selectedYear) return []

  const columns: Column<BiomethaneEnergyMonthlyReportForm>[] = [
    {
      header: t("Mois"),
      cell: (item) => {
        const hoursInMonth = getHoursInMonth(selectedYear, item.month)
        return `${formatMonth(item.month)} (Max : ${formatNumber(hoursInMonth, { fractionDigits: 0 })} h)`
      },
      style: {
        maxWidth: "200px",
      },
    },
    {
      header: t("Volume injecté (Nm³)"),
      cell: (item) => {
        const isError = isInjectionHoursInError(
          selectedYear,
          item.month,
          item.injected_volume_nm3,
          item.average_monthly_flow_nm3_per_hour
        )

        return (
          <NumberInput
            value={item.injected_volume_nm3}
            onChange={(value) =>
              updateCellValue(item.month, "injected_volume_nm3", value)
            }
            min={0}
            readOnly={isReadOnly}
            required
            state={isError ? "error" : "default"}
          />
        )
      },
    },
    {
      header: t("Débit moyen mensuel (Nm³/h)"),
      cell: (item) => {
        const isError = isInjectionHoursInError(
          selectedYear,
          item.month,
          item.injected_volume_nm3,
          item.average_monthly_flow_nm3_per_hour
        )

        return (
          <NumberInput
            value={item.average_monthly_flow_nm3_per_hour}
            onChange={(value) =>
              updateCellValue(
                item.month,
                "average_monthly_flow_nm3_per_hour",
                value
              )
            }
            min={0}
            readOnly={isReadOnly}
            required
            state={isError ? "error" : "default"}
          />
        )
      },
    },
    {
      header: t("Heures d'injection (h)"),
      cell: (item) => {
        const injectionHours = getInjectionHours(
          item.injected_volume_nm3,
          item.average_monthly_flow_nm3_per_hour
        )

        return <TextInput value={formatNumber(injectionHours)} disabled />
      },
    },
  ]

  return columns
}
