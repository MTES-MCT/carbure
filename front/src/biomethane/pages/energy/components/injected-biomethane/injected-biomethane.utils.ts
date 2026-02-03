import { CONVERSIONS, roundNumber } from "common/utils/formatters"
import { BiomethaneEnergyMonthlyReport } from "../../types"

export const getOperatingHoursContract2011Or2020 = (
  injectedNm3PerYear: number,
  cmax: number,
  monthlyReports: BiomethaneEnergyMonthlyReport[]
) => {
  // Calculate the sum of injection hours for all months
  const totalInjectionHours = monthlyReports.reduce((sum, report) => {
    const injectedVolume = report.injected_volume_nm3 ?? 0
    const averageFlow = report.average_monthly_flow_nm3_per_hour ?? 0

    if (averageFlow === 0) return sum

    // Injection hours for this month = injected volume / average flow
    const monthlyInjectionHours = injectedVolume / averageFlow
    return sum + monthlyInjectionHours
  }, 0)

  if (totalInjectionHours === 0) return undefined

  // Calculation: 8760 * Injected quantity (Nm3/year) / (sum of injection hours * Cmax)
  const calculatedHours =
    (CONVERSIONS.hours.yearsToHours(1) * injectedNm3PerYear) /
    (totalInjectionHours * cmax)
  return roundNumber(calculatedHours, 0)
}

export const getInjectedBiomethaneNm3PerYear = (
  gwhPcsPerYear: number,
  pcsKwhPerNm3: number
) => {
  return roundNumber(gwhPcsPerYear * pcsKwhPerNm3 * Math.pow(10, -6), 2)
}
