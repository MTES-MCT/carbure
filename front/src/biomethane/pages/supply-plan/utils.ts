import { BiomethaneSupplyInputSource } from "./types"
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
