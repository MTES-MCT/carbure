import {
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
