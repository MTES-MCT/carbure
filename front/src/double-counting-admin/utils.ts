import { DoubleCountingApplicationDetails } from "double-counting/types"

const FEEDSTOCK_INDUSTRIAL_WASTES_CODES = [
  "DECHETS_INDUSTRIELS",
  "AMIDON_RESIDUEL_DECHETS",
]

/**
 *
 * @param application An application with feedstocks to deduce if there are industrial wastes
 * @returns boolean
 */
export const hasIndustrialWastes = (
  application: DoubleCountingApplicationDetails
) =>
  application.production.filter((a) =>
    FEEDSTOCK_INDUSTRIAL_WASTES_CODES.includes(a.feedstock.code)
  ).length > 0
