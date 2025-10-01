import {
  BiomethaneSupplyInputCategory,
  BiomethaneSupplyInputSource,
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
