import {
  BiomethaneContract,
  InstallationCategory,
  TariffReference,
} from "../types"

export const contractData: BiomethaneContract = {
  tariff_reference: TariffReference.Value2021,
  installation_category: InstallationCategory.INSTALLATION_CATEGORY_1,
  buyer: 1,
  entity: 1,
  amendments: [],
}
