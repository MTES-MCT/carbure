import { EntitySelection } from "common/hooks/helpers/use-entity"
import { SettingsGetter } from "../carbure/hooks"

import use2BSCertificates from "./hooks/use-2bs-certificates"
import useCompany from "./hooks/use-company"
import useDeliverySites from "./hooks/use-delivery-sites"
import useISCCCertificates from "./hooks/use-iscc-certificates"
import useNationalSystemCertificates from "./hooks/use-national-system-certificates"
import useProductionSites from "./hooks/use-production-sites"

export default function useSettings(
  entity: EntitySelection,
  settings: SettingsGetter
) {
  const company = useCompany(entity, settings)
  const productionSites = useProductionSites(entity)
  const deliverySites = useDeliverySites(entity)
  const dbsCertificates = use2BSCertificates(entity, productionSites)
  const isccCertificates = useISCCCertificates(entity, productionSites)
  const nationalSystemCertificates = useNationalSystemCertificates(entity, settings) // prettier-ignore

  return {
    productionSites,
    deliverySites,
    dbsCertificates,
    isccCertificates,
    nationalSystemCertificates,
    company,
  }
}
