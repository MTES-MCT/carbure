import { REDII_CMAX_THRESHOLD, REDII_PAP_THRESHOLD } from "biomethane/config"
import {
  TariffReference,
  BiomethaneContract,
} from "biomethane/pages/contract/types"

export const isTariffReference2011Or2020 = (
  tariff_reference?: TariffReference
) => {
  if (!tariff_reference) return false

  return [TariffReference.Value2011, TariffReference.Value2020].includes(
    tariff_reference
  )
}

export const isTariffReference2021Or2023 = (
  tariff_reference?: TariffReference
) => {
  if (!tariff_reference) return false

  return [TariffReference.Value2021, TariffReference.Value2023].includes(
    tariff_reference
  )
}

export const isContractRedii = (
  contract?: Partial<
    Pick<BiomethaneContract, "tariff_reference" | "cmax" | "pap_contracted">
  >
) => {
  if (!contract) return false

  if (isTariffReference2011Or2020(contract.tariff_reference))
    return contract.cmax && contract.cmax > REDII_CMAX_THRESHOLD

  if (isTariffReference2021Or2023(contract.tariff_reference))
    return (
      contract.pap_contracted && contract.pap_contracted > REDII_PAP_THRESHOLD
    )

  return false
}

/**
 * Gets the appropriate REDII threshold label based on tariff reference
 * @param tariff_reference - The tariff reference to determine the threshold label
 * @returns The threshold label with appropriate units, or empty string if no match
 */
export const getRediiThresholdLabel = (tariff_reference?: TariffReference) => {
  if (isTariffReference2011Or2020(tariff_reference))
    return `${REDII_CMAX_THRESHOLD} Nm³/h`

  if (isTariffReference2021Or2023(tariff_reference))
    return `${REDII_PAP_THRESHOLD} GWhPCS/an`

  return ""
}
