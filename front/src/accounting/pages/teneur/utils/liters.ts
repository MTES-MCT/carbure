import { FRACTION_DIGITS_LITERS } from "accounting/config"
import { ceilNumber } from "common/utils/formatters"
import { mjToDisplayGj } from "./energy"

/** Liters × PCI → MJ (arithmetic) and GJ (display, truncate 3 decimals). */
export const energyFromLiters = (quantityLiters: number, pciLitre: number) => {
  const mj = quantityLiters * pciLitre

  return { mj, gj: mjToDisplayGj(mj) }
}

/** Max declarable liters from remaining cap energy (ceil 2 decimals). */
export const maxLitersFromRemainingMj = (
  remainingEnergyMj: number,
  pciLitre: number
) => ceilNumber(remainingEnergyMj / pciLitre, FRACTION_DIGITS_LITERS)
