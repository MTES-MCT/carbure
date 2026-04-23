import { buildCommonRules } from "./common.rules"
import { BiomethaneRulesContext } from "../types"

export interface DigestateBusinessRules {
  shouldFillDigestate: boolean
}

export const buildDigestateBusinessRules = (
  ctx: BiomethaneRulesContext
): DigestateBusinessRules => {
  const commonRules = buildCommonRules(ctx)

  return {
    shouldFillDigestate: !commonRules.isISDNDInstallation,
  }
}
