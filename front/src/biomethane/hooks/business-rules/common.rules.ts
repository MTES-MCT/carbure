import { BiomethaneRulesContext } from "./types"
import { UnitType } from "biomethane/pages/production/types"
import {
  InstallationCategory,
  TariffReference,
} from "biomethane/pages/contract/types"

export interface CommonBusinessRules {
  isISDNDInstallation: boolean
  isTariffReference2011Or2020Or2021: boolean
}

export const buildCommonRules = (
  ctx: BiomethaneRulesContext
): CommonBusinessRules => {
  const tariffReference = ctx.contractInfos?.tariff_reference
  const isTariffReference2011Or2020Or2021 = tariffReference
    ? [
        TariffReference.Value2011,
        TariffReference.Value2020,
        TariffReference.Value2021,
      ].includes(tariffReference)
    : false

  return {
    isISDNDInstallation:
      ctx.productionUnit?.unit_type === UnitType.ISDND ||
      ctx.contractInfos?.installation_category ===
        InstallationCategory.INSTALLATION_CATEGORY_3,
    isTariffReference2011Or2020Or2021,
  }
}
