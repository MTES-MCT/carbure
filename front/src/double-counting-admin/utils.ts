import { DoubleCountingApplicationDetails } from "double-counting/types"

/**
 *
 * @param application An application with feedstocks to deduce if there are industrial wastes
 * @returns boolean
 */
export const hasIndustrialWastes = (
  application: DoubleCountingApplicationDetails
) => application.production.some((a) => a.feedstock.is_industrial_waste)
