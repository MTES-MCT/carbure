import { DepotType, OwnershipType } from "carbure/types"
import i18next from "i18next"

export const depotTypeLabels = {
  [DepotType.EFS]: i18next.t("EFS"),
  [DepotType.EFPE]: i18next.t("EFPE"),
  [DepotType.Other]: i18next.t("Autre"),
  [DepotType.BiofuelDepot]: i18next.t("Dépôt de biocarburant"),
  [DepotType.OilDepot]: i18next.t("Dépôt pétrolier"),
  [DepotType.PowerPlant]: i18next.t("Centrale électrique"),
  [DepotType.HeatPlant]: i18next.t("Centrale de chaleur"),
  [DepotType.CogenerationPlant]: i18next.t("Centrale de cogénération"),
}

export const depotTypeOptions = Object.entries(depotTypeLabels).map(
  ([value, label]) => ({ label, value })
)

export const ownerShipTypeOptions = [
  { value: OwnershipType.Own, label: i18next.t("Propre") },
  { value: OwnershipType.ThirdParty, label: i18next.t("Tiers") },
  { value: OwnershipType.Processing, label: i18next.t("Processing") },
]
