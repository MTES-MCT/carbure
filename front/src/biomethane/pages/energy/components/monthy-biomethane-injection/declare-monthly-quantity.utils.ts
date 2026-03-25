export const INJECTION_HOURS_EPSILON = 1e-6

export const getInjectionHours = (
  injectedVolumeNm3?: number,
  averageMonthlyFlowNm3PerHour?: number
) => {
  if (!injectedVolumeNm3 || !averageMonthlyFlowNm3PerHour) return 0
  return injectedVolumeNm3 / averageMonthlyFlowNm3PerHour
}

export const getHoursInMonth = (year: number, month: number) => {
  // month: 1..12
  const daysInMonth = new Date(year, month, 0).getDate()
  return daysInMonth * 24
}
