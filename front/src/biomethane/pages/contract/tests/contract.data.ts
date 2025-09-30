import {
  BiomethaneContract,
  InstallationCategory,
  TariffReference,
} from "../types"

export const contractData: BiomethaneContract = {
  id: 1,
  tariff_reference: TariffReference.Value2021,
  installation_category: InstallationCategory.INSTALLATION_CATEGORY_1,
  buyer: 1,
  producer: 1,
  amendments: [],
  tracked_amendment_types: [],
}
