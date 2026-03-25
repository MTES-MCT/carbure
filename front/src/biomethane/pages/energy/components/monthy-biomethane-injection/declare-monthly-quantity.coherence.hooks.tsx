import { useTranslation } from "react-i18next"
import { formatMonth, formatNumber } from "common/utils/formatters"
import {
  getHoursInMonth,
  getInjectionHours,
  INJECTION_HOURS_EPSILON,
} from "./declare-monthly-quantity.utils"

type MonthlyReportRow = {
  month: number
  injected_volume_nm3?: number
  average_monthly_flow_nm3_per_hour?: number
}

export type InjectionHoursCoherenceError = {
  monthLabel: string
  injectionHours: number
  monthHours: number
}

export const useInjectionHoursCoherence = () => {
  const { t } = useTranslation()

  const validateInjectionHoursCoherence = (
    rows: MonthlyReportRow[],
    selectedYear: number
  ): InjectionHoursCoherenceError[] => {
    const errors: InjectionHoursCoherenceError[] = []

    for (const item of rows) {
      const injectionHours = getInjectionHours(
        item.injected_volume_nm3,
        item.average_monthly_flow_nm3_per_hour
      )

      if (!Number.isFinite(injectionHours)) continue

      const hoursInMonth = getHoursInMonth(selectedYear, item.month)
      if (injectionHours > hoursInMonth + INJECTION_HOURS_EPSILON) {
        errors.push({
          monthLabel: formatMonth(item.month),
          injectionHours,
          monthHours: hoursInMonth,
        })
      }
    }

    return errors
  }

  const buildInjectionHoursCoherenceErrorMessage = (
    errors: InjectionHoursCoherenceError[]
  ) => {
    return (
      <>
        <div>
          {t(
            "Les heures d'injection calculées sont supérieures au nombre d'heures du mois :"
          )}
        </div>
        <ul>
          {errors.map((error) => (
            <li key={error.monthLabel}>
              {t("{{month}} : {{injectionHours}} h (Max {{monthHours}} h)", {
                month: error.monthLabel,
                injectionHours: formatNumber(error.injectionHours),
                monthHours: formatNumber(error.monthHours, {
                  fractionDigits: 0,
                }),
              })}
            </li>
          ))}
        </ul>
      </>
    )
  }

  return {
    validateInjectionHoursCoherence,
    buildInjectionHoursCoherenceErrorMessage,
  }
}
