import { Country, DepotType, OwnershipType } from "carbure/types"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"

export const useDeliverySiteFlags = (depotType?: DepotType) =>
  useMemo(
    () => ({
      isPowerPlant: depotType === DepotType.PowerPlant,
      isHeatPlant: depotType === DepotType.HeatPlant,
      isCogenerationPlant: depotType === DepotType.CogenerationPlant,
    }),
    [depotType]
  )

export const useDepotTypeLabels = () => {
  const { t } = useTranslation()

  return useMemo(
    () => ({
      [DepotType.EFS]: t("EFS"),
      [DepotType.EFPE]: t("EFPE"),
      [DepotType.Other]: t("Autre"),
      [DepotType.BiofuelDepot]: t("Biofuel Depot"),
      [DepotType.OilDepot]: t("Oil Depot"),
      [DepotType.PowerPlant]: t("Centrale électrique"),
      [DepotType.HeatPlant]: t("Centrale de chaleur"),
      [DepotType.CogenerationPlant]: t("Centrale de cogénération"),
    }),
    [t]
  )
}

export const useGetDepotTypeOptions = (country?: Country) => {
  const depotTypeLabels = useDepotTypeLabels()

  return useMemo(() => {
    const depotTypeOptions = Object.entries(depotTypeLabels).map(
      ([value, label]) => ({ label, value })
    )

    // If the country selected in the form is France, we have to remove Oil/Biofuel depot
    if (!country || country?.code_pays === "FR") {
      return depotTypeOptions.filter(
        ({ value }) =>
          ![DepotType.OilDepot, DepotType.BiofuelDepot].includes(
            value as DepotType
          )
      )
    }
    return depotTypeOptions
  }, [country, depotTypeLabels])
}

export const useOwnerShipTypeOptions = () => {
  const { t } = useTranslation()

  return useMemo(
    () => [
      { value: OwnershipType.Own, label: t("Propre") },
      { value: OwnershipType.ThirdParty, label: t("Tiers") },
      { value: OwnershipType.Processing, label: t("Processing") },
    ],
    [t]
  )
}
