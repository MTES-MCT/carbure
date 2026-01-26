import {
  BiomethaneSupplyInputCategory,
  BiomethaneSupplyInputCropType,
  BiomethaneSupplyInputSource,
  BiomethaneSupplyInputMaterialUnit,
} from "./types"
import i18next from "i18next"

export const getSupplyPlanInputSource = (
  source: BiomethaneSupplyInputSource
) => {
  switch (source) {
    case BiomethaneSupplyInputSource.INTERNAL:
      return i18next.t("Interne")
    case BiomethaneSupplyInputSource.EXTERNAL:
      return i18next.t("Externe")
  }
}

export const getSupplyPlanInputCategory = (
  category: BiomethaneSupplyInputCategory
) => {
  switch (category) {
    case BiomethaneSupplyInputCategory.LIVESTOCK_EFFLUENTS:
      return i18next.t("Effluents d'élevage")
    case BiomethaneSupplyInputCategory.PRIMARY_CROPS:
      return i18next.t("Culture principale")
    case BiomethaneSupplyInputCategory.INTERMEDIATE_CROPS:
      return i18next.t("Culture intermédiaire")
    case BiomethaneSupplyInputCategory.CIVE:
      return i18next.t("CIVE")
    case BiomethaneSupplyInputCategory.IAA_WASTE_RESIDUES:
      return i18next.t("Déchets/Résidus d'IAA")
  }
}

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

export const getSupplyPlanInputCategoryOptions = () => {
  return [
    {
      value: BiomethaneSupplyInputCategory.LIVESTOCK_EFFLUENTS,
      label: i18next.t("Effluents d'élevage"),
    },
    {
      value: BiomethaneSupplyInputCategory.PRIMARY_CROPS,
      label: i18next.t("Culture principale"),
    },
    {
      value: BiomethaneSupplyInputCategory.INTERMEDIATE_CROPS,
      label: i18next.t("Culture intermédiaire"),
    },
    { value: BiomethaneSupplyInputCategory.CIVE, label: i18next.t("CIVE") },
    {
      value: BiomethaneSupplyInputCategory.IAA_WASTE_RESIDUES,
      label: i18next.t("Déchets/Résidus d'IAA"),
    },
  ]
}

export const getSupplyPlanInputCropTypeOptions = () => {
  return [
    {
      value: BiomethaneSupplyInputCropType.MAIN,
      label: i18next.t("Principale"),
    },
    {
      value: BiomethaneSupplyInputCropType.INTERMEDIATE,
      label: i18next.t("Intermédiaire"),
    },
  ]
}

export const getSupplyPlanInputMaterialUnitOptions = () => {
  return [
    { value: BiomethaneSupplyInputMaterialUnit.DRY, label: i18next.t("Sèche") },
    { value: BiomethaneSupplyInputMaterialUnit.WET, label: i18next.t("Brute") },
  ]
}

export const convertSupplyPlanInputVolume = (
  volumeTonsMS: number,
  ratioTonsMS: number
) => {
  const ratioTonsMB = 100 - ratioTonsMS

  return volumeTonsMS / ratioTonsMS / ratioTonsMB
}
