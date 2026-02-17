import { describe, expect, it } from "vitest"
import { BiomethaneEnergyMonthlyReport } from "../../types"
import { getOperatingHoursContract2011Or2020 } from "./injected-biomethane.utils"

const report = (
  overrides: Partial<BiomethaneEnergyMonthlyReport> = {}
): BiomethaneEnergyMonthlyReport =>
  ({
    month: 1,
    energy: 0,
    ...overrides,
  }) as BiomethaneEnergyMonthlyReport

describe("getOperatingHoursContract2011Or2020", () => {
  it("Returns undefined when there are no monthly reports (prevent division by 0)", () => {
    const result = getOperatingHoursContract2011Or2020(1000, 5, [])
    expect(result).toBeUndefined()
  })

  it("Returns undefined when all monthly reports have an average flow of 0 (prevent division by 0)", () => {
    const monthlyReports: BiomethaneEnergyMonthlyReport[] = [
      report({
        month: 1,
        injected_volume_nm3: 100,
        average_monthly_flow_nm3_per_hour: 0,
      }),
      report({
        month: 2,
        injected_volume_nm3: 200,
        average_monthly_flow_nm3_per_hour: 0,
      }),
    ]
    const result = getOperatingHoursContract2011Or2020(1000, 5, monthlyReports)
    expect(result).toBeUndefined()
  })

  it("Sums the injection hours over multiple months", () => {
    // Month 1 : 100/10 = 10 h, Month 2 : 200/20 = 10 h → totalInjectionHours = 20
    const monthlyReports: BiomethaneEnergyMonthlyReport[] = [
      report({
        month: 1,
        injected_volume_nm3: 100,
        average_monthly_flow_nm3_per_hour: 10,
      }),
      report({
        month: 2,
        injected_volume_nm3: 200,
        average_monthly_flow_nm3_per_hour: 20,
      }),
    ]
    // 8760 * 1000 / (20 * 5) = 87600
    const result = getOperatingHoursContract2011Or2020(1000, 5, monthlyReports)
    expect(result).toBe(87600)
  })

  it("Rounds the result to the nearest integer (0 decimal places)", () => {
    const monthlyReports: BiomethaneEnergyMonthlyReport[] = [
      report({
        month: 1,
        injected_volume_nm3: 33,
        average_monthly_flow_nm3_per_hour: 11,
      }),
    ]
    // totalInjectionHours = 3, 8760 * 100 / (3 * 1) = 292000
    const result = getOperatingHoursContract2011Or2020(100, 1, monthlyReports)
    expect(result).toBe(292000)
  })
})
