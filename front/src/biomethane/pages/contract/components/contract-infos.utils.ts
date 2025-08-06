import { TariffReference } from "biomethane/types"

export const isTariffReference2011Or2020 = (
  tariff_reference?: TariffReference
) => {
  if (!tariff_reference) return false

  return [TariffReference.Value2011, TariffReference.Value2020].includes(
    tariff_reference
  )
}
