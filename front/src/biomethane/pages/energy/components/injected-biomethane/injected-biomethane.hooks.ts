import { useEffect, useMemo } from "react"
import { BiomethaneContract } from "biomethane/pages/contract/types"
import {
  isTariffReference2011Or2020,
  isTariffReference2021Or2023,
} from "biomethane/pages/contract/contract.utils"
import { InjectedBiomethaneForm } from "./injected-biomethane"
import { useFormContext } from "common/components/form2"
import { roundNumber } from "common/utils/formatters"
import { BiomethaneEnergyMonthlyReport } from "../../types"
import { useTranslation } from "react-i18next"

/**
 * Calculates operating hours according to the rules:
 * - For contracts 2011 and 2020: "Injected biomethane quantity (Nm3/year)" / (sum of injection hours * contract Cmax)
 * - For contracts 2021 and 2023: "Injected biomethane quantity (GWh PCS/year)" / "contract PAP"
 */
export const useInjectedBiomethane = (
  monthlyReports: BiomethaneEnergyMonthlyReport[],
  contract?: BiomethaneContract
) => {
  const { value: energy, setField } = useFormContext<InjectedBiomethaneForm>()
  const { t } = useTranslation()

  const operatingHours = useMemo(() => {
    if (!energy || !contract) return undefined

    const tariffReference = contract.tariff_reference

    // For contracts 2011 and 2020
    if (isTariffReference2011Or2020(tariffReference)) {
      const injectedNm3PerYear = energy.injected_biomethane_nm3_per_year
      const cmax = contract.cmax

      if (!injectedNm3PerYear || !cmax || !monthlyReports) return undefined

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

      // Calculation: Injected quantity (Nm3/year) / (sum of injection hours * Cmax)
      const calculatedHours = injectedNm3PerYear / (totalInjectionHours * cmax)
      return roundNumber(calculatedHours, 0)
    }

    // For contracts 2021 and 2023
    if (isTariffReference2021Or2023(tariffReference)) {
      const injectedGwhPcsPerYear = energy.injected_biomethane_gwh_pcs_per_year
      const papContracted = contract.pap_contracted

      if (!injectedGwhPcsPerYear || !papContracted) return undefined

      // Calculation: Injected quantity (GWh PCS/year) / contract PAP
      const calculatedHours = injectedGwhPcsPerYear / papContracted
      return roundNumber(calculatedHours, 0)
    }

    return undefined
  }, [energy, contract, monthlyReports])

  const rule = useMemo(() => {
    if (!energy || !contract) return undefined

    const tariffReference = contract.tariff_reference

    if (isTariffReference2011Or2020(tariffReference)) {
      return t(
        "Quantité de biométhane injectée (Nm3/an) / (somme du nombre d'heures d'injection [du tableau renseigné dans la section Production mensuelle de biométhane] * Cmax du contrat)"
      )
    }

    return t("Quantité de biométhane injectée (GWh PCS/an) / PAP du contrat")
  }, [energy, contract, t])

  // Set the operating hours in the form when it is calculated
  useEffect(() => {
    if (operatingHours) {
      setField("operating_hours", operatingHours)
    }
  }, [operatingHours, setField])

  return {
    operatingHours,
    rule,
  }
}
