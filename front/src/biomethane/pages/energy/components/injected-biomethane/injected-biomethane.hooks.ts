import { useMemo } from "react"
import { BiomethaneContract } from "biomethane/pages/contract/types"
import {
  isTariffReference2011Or2020,
  isTariffReference2021Or2023,
} from "biomethane/pages/contract/contract.utils"
import { InjectedBiomethaneForm } from "./injected-biomethane"
import { useFormContext } from "common/components/form2"
import { CONVERSIONS, roundNumber } from "common/utils/formatters"
import { BiomethaneEnergyMonthlyReport } from "../../types"
import { useTranslation } from "react-i18next"
import {
  getInjectedBiomethaneNm3PerYear,
  getOperatingHoursContract2011Or2020,
} from "./injected-biomethane.utils"

/**
 * Calculates operating hours according to the rules:
 * - For contracts 2011 and 2020: "8760 * Quantité de biométhane injectée (Nm3/an)" / (somme du nombre d'heures d'injection [du tableau section Production mensuelle de biométhane] * Cmax du contrat)
 * - For contracts 2021 and 2023: "8760 * Quantité de biométhane injectée (GWh PCS/an)" / "PAP du contrat"
 */
export const useOperatingHours = (
  monthlyReports: BiomethaneEnergyMonthlyReport[],
  contract?: BiomethaneContract
) => {
  const { value: energy } = useFormContext<InjectedBiomethaneForm>()
  const { injectedBiomethaneNm3PerYear } = useInjectedBiomethaneNm3PerYear()
  const { t } = useTranslation()

  const operatingHours = useMemo(() => {
    if (!energy || !contract) return undefined

    const tariffReference = contract.tariff_reference

    // For contracts 2011 and 2020
    if (isTariffReference2011Or2020(tariffReference)) {
      const cmax = contract.cmax

      if (!injectedBiomethaneNm3PerYear || !cmax || !monthlyReports)
        return undefined

      return getOperatingHoursContract2011Or2020(
        injectedBiomethaneNm3PerYear,
        cmax,
        monthlyReports
      )
    }

    // For contracts 2021 and 2023
    if (isTariffReference2021Or2023(tariffReference)) {
      const injectedGwhPcsPerYear = energy.injected_biomethane_gwh_pcs_per_year
      const papContracted = contract.pap_contracted

      if (!injectedGwhPcsPerYear || !papContracted) return undefined

      // Calculation: 8760 * Injected quantity (GWh PCS/year) / contract PAP
      const calculatedHours =
        (CONVERSIONS.hours.yearsToHours(1) * injectedGwhPcsPerYear) /
        papContracted
      return roundNumber(calculatedHours, 0)
    }

    return undefined
  }, [energy, contract, monthlyReports, injectedBiomethaneNm3PerYear])

  const rule = useMemo(() => {
    if (!energy || !contract) return undefined

    const tariffReference = contract.tariff_reference

    if (isTariffReference2011Or2020(tariffReference)) {
      return t(
        "8760 * Quantité de biométhane injectée (Nm3/an) / (somme du nombre d'heures d'injection [du tableau renseigné dans la section Production mensuelle de biométhane] * Cmax du contrat)"
      )
    }

    return t(
      "8760 * Quantité de biométhane injectée (GWh PCS/an) / PAP du contrat"
    )
  }, [energy, contract, t])

  return {
    operatingHours,
    rule,
  }
}

const useInjectedBiomethaneNm3PerYear = () => {
  const { value: energy } = useFormContext<InjectedBiomethaneForm>()

  const injectedBiomethaneNm3PerYear = useMemo(() => {
    return roundNumber(
      getInjectedBiomethaneNm3PerYear(
        energy.injected_biomethane_gwh_pcs_per_year ?? 0,
        energy.injected_biomethane_pcs_kwh_per_nm3 ?? 0
      ),
      2
    )
  }, [energy])

  return {
    injectedBiomethaneNm3PerYear,
  }
}

export const useInjectedBiomethane = (
  monthlyReports: BiomethaneEnergyMonthlyReport[],
  contract?: BiomethaneContract
) => {
  const operatingHoursData = useOperatingHours(monthlyReports, contract)
  const injectedBiomethaneNm3PerYearData = useInjectedBiomethaneNm3PerYear()

  return {
    ...operatingHoursData,
    ...injectedBiomethaneNm3PerYearData,
  }
}
