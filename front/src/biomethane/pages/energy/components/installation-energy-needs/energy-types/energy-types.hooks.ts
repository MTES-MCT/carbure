import {
  BiomethaneContract,
  InstallationCategory,
  TariffReference,
} from "biomethane/pages/contract/types"
import { EnergyType } from "biomethane/pages/energy/types"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"

export const useEnergyTypeLabel = (
  tariffReference?: TariffReference | null
) => {
  const { t } = useTranslation()

  const label = useMemo(() => {
    switch (tariffReference) {
      case TariffReference.Value2023:
        return t(
          "Type d'énergie utilisée pour la pasteurisation, l'hygiénisation et le prétraitement des intrants, le chauffage du digesteur et l’épuration du biogaz"
        )
      default:
        return t("Type d'énergie utilisée pour le chauffage du digesteur")
    }
  }, [tariffReference, t])

  return label
}

export const useEnergyTypeOptions = (contract?: BiomethaneContract) => {
  const { t } = useTranslation()

  const allOptions = useMemo(
    () => ({
      [EnergyType.PRODUCED_BIOGAS]: t("Biogaz produit par l'installation"),
      [EnergyType.PRODUCED_BIOMETHANE]: t(
        "Biométhane produit par l'installation"
      ),
      [EnergyType.WASTE_HEAT_PREEXISTING]: t(
        "Chaleur fatale [Energie thermique résiduelle] (issue d'un équipement préexistant installé sur site ou sur un site situé à proximité)"
      ),
      [EnergyType.WASTE_HEAT_PURIFICATION]: t(
        "Chaleur fatale (issue du système d'épuration ou de compression de l'installation)"
      ),
      [EnergyType.WASTE_HEAT_ON_SITE]: t(
        "Chaleur fatale (issue d'un équipement installé sur site)"
      ),
      [EnergyType.BIOMASS_BOILER]: t("Chaudière biomasse"),
      [EnergyType.SOLAR_THERMAL]: t("Solaire thermique"),
      [EnergyType.OTHER_RENEWABLE]: t("Autre énergie renouvelable"),
      [EnergyType.FOSSIL]: t("Energie fossile"),
      [EnergyType.OTHER]: t("Autre"),
    }),
    [t]
  )

  const optionsToKeep = useMemo(() => {
    const commonOptions = [
      EnergyType.PRODUCED_BIOGAS,
      EnergyType.PRODUCED_BIOMETHANE,
    ]
    const wasteHeatPurificationOption =
      contract?.installation_category ===
      InstallationCategory.INSTALLATION_CATEGORY_2
        ? [EnergyType.WASTE_HEAT_ON_SITE]
        : []

    switch (contract?.tariff_reference) {
      case TariffReference.Value2023:
        return [
          ...commonOptions,
          EnergyType.WASTE_HEAT_PURIFICATION,
          ...wasteHeatPurificationOption,
          EnergyType.BIOMASS_BOILER,
          EnergyType.SOLAR_THERMAL,
          EnergyType.OTHER_RENEWABLE,
          EnergyType.FOSSIL,
        ]
      case TariffReference.Value2011:
        return [
          ...commonOptions,
          EnergyType.WASTE_HEAT_PREEXISTING,
          EnergyType.OTHER,
        ]
      default:
        return [
          ...commonOptions,
          EnergyType.WASTE_HEAT_PURIFICATION,
          ...wasteHeatPurificationOption,
          EnergyType.OTHER,
        ]
    }
  }, [contract?.tariff_reference, contract?.installation_category])

  const optionsForContract = useMemo(() => {
    return Object.entries(allOptions)
      .filter(([key]) => optionsToKeep.includes(key as EnergyType))
      .map(([key, value]) => ({
        value: key,
        label: value,
      }))
  }, [allOptions, optionsToKeep])

  return optionsForContract
}
