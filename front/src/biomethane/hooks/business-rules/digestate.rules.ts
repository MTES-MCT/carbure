import { BiomethaneRulesContext } from "./types"
import { buildCommonRules } from "./common.rules"

export interface DigestateBusinessRules {
  shouldFillDigestate: boolean
}

/**
 * Digestate page must be filled unless:
 * - production unit type is ISDND
 * - or contract installation category is 3
 */
export const buildDigestateBusinessRules = (
  ctx: BiomethaneRulesContext
): DigestateBusinessRules => {
  const commonRules = buildCommonRules(ctx)
  return {
    shouldFillDigestate: commonRules.isISDNDInstallation,
  }
}
