import { useTranslation } from "react-i18next"
import { formatMonth } from "common/utils/formatters"
import { isInjectionHoursInError } from "./declare-monthly-quantity.utils"

type MonthlyReportRow = {
  month: number
  injected_volume_nm3?: number
  average_monthly_flow_nm3_per_hour?: number
}

export const useInjectionHoursCoherence = () => {
  const { t } = useTranslation()

  const validateInjectionHoursCoherence = (
    rows: MonthlyReportRow[],
    selectedYear: number
  ): string[] => {
    const errors: string[] = []

    for (const item of rows) {
      if (
        isInjectionHoursInError(
          selectedYear,
          item.month,
          item.injected_volume_nm3,
          item.average_monthly_flow_nm3_per_hour
        )
      ) {
        errors.push(formatMonth(item.month))
      }
    }

    return errors
  }

  const buildInjectionHoursCoherenceErrorMessage = (month: string[]) => {
    const monthsList = month.join(", ")

    return (
      <div>
        {t(
          "Les heures d'injection calculées sont supérieures au nombre d'heures dans les mois suivants : {{months}}",
          { months: monthsList }
        )}
      </div>
    )
  }

  return {
    validateInjectionHoursCoherence,
    buildInjectionHoursCoherenceErrorMessage,
  }
}
