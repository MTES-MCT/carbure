import {
  ENERGY_EFFICIENCY_COEFFICIENT_THRESHOLD_KWHE_NM3,
  ENERGY_EFFICIENCY_COEFFICIENT_THRESHOLD_MWHE_MWHPCS,
} from "biomethane/config"
import { TariffReference } from "biomethane/pages/contract/types"
import { formatNumber } from "common/utils/formatters"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"

type CalculateEnergyEfficiencyCoefficientData = {
  purified_biogas_quantity_nm3: number
  purification_electric_consumption_kwe: number
  total_unit_electric_consumption_kwe: number
  tariff_reference?: TariffReference
  injected_biomethane_gwh_pcs_per_year: number
}
export function calculateEnergyEfficiencyCoefficient({
  purified_biogas_quantity_nm3,
  purification_electric_consumption_kwe,
  total_unit_electric_consumption_kwe,
  tariff_reference,
  injected_biomethane_gwh_pcs_per_year,
}: CalculateEnergyEfficiencyCoefficientData) {
  if (
    !tariff_reference ||
    purified_biogas_quantity_nm3 === 0 ||
    injected_biomethane_gwh_pcs_per_year === 0
  )
    return 0

  const isTariffReference2023 = tariff_reference === TariffReference.Value2023

  if (isTariffReference2023) {
    return (
      total_unit_electric_consumption_kwe / injected_biomethane_gwh_pcs_per_year
    )
  }

  return purification_electric_consumption_kwe / purified_biogas_quantity_nm3
}

export const useEnergyEfficiencyCoefficient = ({
  purified_biogas_quantity_nm3,
  purification_electric_consumption_kwe,
  total_unit_electric_consumption_kwe,
  tariff_reference,
  injected_biomethane_gwh_pcs_per_year,
}: CalculateEnergyEfficiencyCoefficientData) => {
  const { t } = useTranslation()

  const energyEfficiencyCoefficient = useMemo(() => {
    const value = calculateEnergyEfficiencyCoefficient({
      purified_biogas_quantity_nm3,
      purification_electric_consumption_kwe,
      total_unit_electric_consumption_kwe,
      tariff_reference,
      injected_biomethane_gwh_pcs_per_year:
        injected_biomethane_gwh_pcs_per_year,
    })

    if (tariff_reference === TariffReference.Value2023) {
      return {
        value,
        label: `${formatNumber(value, { fractionDigits: 2 })} ${t("MWhe/MWhPCS de biométhane injecté")}`,
        error:
          value > ENERGY_EFFICIENCY_COEFFICIENT_THRESHOLD_MWHE_MWHPCS
            ? t(
                "La condition d’efficacité énergétique n’est pas respectée (supérieur à {{value}} MWhe/MWhPCS de biométhane injecté)",
                {
                  value: ENERGY_EFFICIENCY_COEFFICIENT_THRESHOLD_MWHE_MWHPCS,
                }
              )
            : undefined,
      }
    }

    return {
      value,
      label: `${formatNumber(value, { fractionDigits: 2 })} ${t("kWhe/Nm³ de biogaz à traiter")}`,
      error:
        value > ENERGY_EFFICIENCY_COEFFICIENT_THRESHOLD_KWHE_NM3
          ? t(
              "La condition d’efficacité énergétique n’est pas respectée (supérieur à {{value}} KWhe/Nm3)",
              {
                value: ENERGY_EFFICIENCY_COEFFICIENT_THRESHOLD_KWHE_NM3,
              }
            )
          : undefined,
    }
  }, [
    purified_biogas_quantity_nm3,
    purification_electric_consumption_kwe,
    total_unit_electric_consumption_kwe,
    tariff_reference,
    injected_biomethane_gwh_pcs_per_year,
    t,
  ])

  return energyEfficiencyCoefficient
}
