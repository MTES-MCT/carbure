import { FRACTION_DIGITS_LITERS } from "accounting/config"
import { ceilNumber } from "common/utils/formatters"
import { mjToDisplayGj } from "./energy"

/** Renewable energy in MJ and GJ from a physical volume in liters. */
/** Liters x PCI per liter x renewable energy share -> MJ (arithmetic) and GJ (display, truncate 3 decimals) */
export const energyFromLiters = (
  quantityLiters: number,
  pciLitre: number,
  renewableEnergyShare = 1
) => {
  const mj = quantityLiters * pciLitre * renewableEnergyShare

  return { mj, gj: mjToDisplayGj(mj) }
}

/** Max declarable liters from remaining cap energy (ceil 2 decimals). */
export const maxLitersFromRemainingMj = (
  remainingEnergyMj: number,
  pciLitre: number,
  renewableEnergyShare = 1
) =>
  ceilNumber(
    remainingEnergyMj / (pciLitre * renewableEnergyShare),
    FRACTION_DIGITS_LITERS
  )
