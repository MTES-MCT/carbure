import { DoubleCountingApplicationDetails } from "double-counting/types"

const FEEDSTOCK_INDUSTRIAL_WASTES_CODE = "DECHETS_INDUSTRIELS"

/**
 *
 * @param application An application with feedstocks to deduce if there are industrial wastes
 * @returns boolean
 */
export const hasIndustrialWastes = (
  application: DoubleCountingApplicationDetails
) =>
  application.production.filter(
    (a) => a.feedstock.code === FEEDSTOCK_INDUSTRIAL_WASTES_CODE
  ).length > 0
