import {
  BiomethaneSupplyInputMaterialUnit,
  BiomethaneSupplyInputTypeCive,
  BiomethaneSupplyInputCollectionType,
  BiomethaneSupplyInputSource,
} from "./types"
import i18next from "i18next"

/** Input names (intrant) that require "Type de collecte" to be filled */
export const SUPPLY_PLAN_INPUT_NAMES_REQUIRING_COLLECTION_TYPE = [
  "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-ANIMALE",
  "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-VEGETALE",
  "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-NON-SPECIFIEE",
  "GRAISSES-DE-BACS-A-GRAISSE-DE-RESTAURATION",
  "AUTRE-DECHETS-GRAISSEUX",
  "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-1",
  "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-2",
  "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-3",
]

export const getSupplyPlanInputSourceOptions = () => {
  return [
    {
      value: BiomethaneSupplyInputSource.INTERNAL,
      label: i18next.t("Interne"),
    },
    {
      value: BiomethaneSupplyInputSource.EXTERNAL,
      label: i18next.t("Externe"),
    },
  ]
}

export const getSupplyPlanInputMaterialUnitOptions = () => {
  return [
    { value: BiomethaneSupplyInputMaterialUnit.DRY, label: i18next.t("Sèche") },
    { value: BiomethaneSupplyInputMaterialUnit.WET, label: i18next.t("Brute") },
  ]
}

export const getSupplyPlanInputTypeCiveOptions = () => {
  return [
    { value: BiomethaneSupplyInputTypeCive.SUMMER, label: i18next.t("Été") },
    { value: BiomethaneSupplyInputTypeCive.WINTER, label: i18next.t("Hiver") },
  ]
}

export const getSupplyPlanInputCollectionTypeOptions = () => {
  return [
    {
      value: BiomethaneSupplyInputCollectionType.PRIVATE,
      label: i18next.t("Issus de collecteurs privés"),
    },
    {
      value: BiomethaneSupplyInputCollectionType.LOCAL,
      label: i18next.t("Issus de collectivités locales"),
    },
    {
      value: BiomethaneSupplyInputCollectionType.BOTH,
      label: i18next.t("Issus des collectivités locales et collecteurs privés"),
    },
  ]
}

export const convertSupplyPlanInputVolume = (
  volumeTonsMS: number,
  ratioTonsMS: number
) => {
  const ratioTonsMB = 100 - ratioTonsMS

  return volumeTonsMS / ratioTonsMS / ratioTonsMB
}
