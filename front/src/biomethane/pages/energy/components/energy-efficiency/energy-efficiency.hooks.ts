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
  tariff_reference?: TariffReference | null
  injected_biomethane_gwh_pcs_per_year: number
}

/**
 * Selon la valeur de la référence tarifaire (défini dans le contrat), on calcule l'efficacité énergétique
 * en fonction de différents paramètres.
 * Si tariff_reference = 2023, le coefficient d'efficacité énergétique est calculé en fonction de :
 *    - la consommation électrique soutirée pour l'ensemble de l'unité (kWe)
 *    - la quantité de biométhane injecté (GWhPCS/an)
 * Si tariff_reference = 2021, le coefficient d'efficacité énergétique est calculé en fonction de :
 *    - la consommation électrique du système d'épuration et le cas échéant du traitement des évents (kWe)
 *    - la quantité totale de biogaz traitée par le système d'épuration sur l’année (Nm3)
 */
export function calculateEnergyEfficiencyCoefficient({
  purified_biogas_quantity_nm3,
  purification_electric_consumption_kwe,
  total_unit_electric_consumption_kwe,
  tariff_reference,
  injected_biomethane_gwh_pcs_per_year,
}: CalculateEnergyEfficiencyCoefficientData) {
  if (!tariff_reference) return 0

  const isTariffReference2023 = tariff_reference === TariffReference.Value2023

  // Handle divide by 0
  if (purified_biogas_quantity_nm3 === 0 && !isTariffReference2023) return 0

  // Handle divide by 0
  if (injected_biomethane_gwh_pcs_per_year === 0 && isTariffReference2023)
    return 0

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
        tooltip: t(
          "Le coefficient d'efficacité énergétique est calculé en fonction de la consommation électrique soutirée pour l'ensemble de l'unité (kWe) divisé par la quantité de biométhane injecté (GWhPCS/an)."
        ),
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
      tooltip: t(
        "Le coefficient d'efficacité énergétique est calculé en fonction de la consommation électrique du système d'épuration et le cas échéant du traitement des évents (kWe) divisé par la quantité totale de biogaz traitée par le système d'épuration sur l’année (Nm3)."
      ),
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
