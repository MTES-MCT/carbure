import { TariffReference } from "biomethane/pages/contract/types"

export const isTariffReference2011 = (
  tariffReference?: TariffReference | null
) => tariffReference === TariffReference.Value2011

export const isTariffReference2020Plus = (
  tariffReference?: TariffReference | null
) => {
  if (!tariffReference) return false

  return [
    TariffReference.Value2020,
    TariffReference.Value2021,
    TariffReference.Value2023,
  ].includes(tariffReference)
}
