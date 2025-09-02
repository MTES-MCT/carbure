import { describe, expect, it } from "vitest"
import { calculateEnergyEfficiencyCoefficient } from "./energy-efficiency.hooks"
import { TariffReference } from "biomethane/pages/contract/types"

const baseData = {
  purified_biogas_quantity_nm3: 0,
  purification_electric_consumption_kwe: 0,
  total_unit_electric_consumption_kwe: 0,
  tariff_reference: undefined,
  injected_biomethane_gwh_pcs_per_year: 0,
}
describe("calculateEnergyEfficiencyCoefficient", () => {
  it("should return 0 if the tariff reference is not provided", () => {
    const result = calculateEnergyEfficiencyCoefficient(baseData)

    expect(result).toBe(0)
  })

  it("should return 0 if the purified biogas quantity is 0 and the tariff reference is not 2023", () => {
    const result = calculateEnergyEfficiencyCoefficient({
      ...baseData,
      tariff_reference: TariffReference.Value2021,
    })

    expect(result).toBe(0)
  })

  it("should return 0 if the injected biomethane gwh pcs per year is 0 and the tariff reference is 2023", () => {
    const result = calculateEnergyEfficiencyCoefficient({
      ...baseData,
      tariff_reference: TariffReference.Value2023,
      injected_biomethane_gwh_pcs_per_year: 0,
    })

    expect(result).toBe(0)
  })

  it("should return the correct energy efficiency coefficient if the tariff reference is 2023", () => {
    const result = calculateEnergyEfficiencyCoefficient({
      ...baseData,
      tariff_reference: TariffReference.Value2023,
      total_unit_electric_consumption_kwe: 100,
      injected_biomethane_gwh_pcs_per_year: 100,
    })

    expect(result).toBe(1)
  })

  it("should return the correct energy efficiency coefficient if the tariff reference is 2021", () => {
    const result = calculateEnergyEfficiencyCoefficient({
      ...baseData,
      tariff_reference: TariffReference.Value2021,
      purified_biogas_quantity_nm3: 100,
      purification_electric_consumption_kwe: 200,
    })

    expect(result).toBe(2)
  })
})
