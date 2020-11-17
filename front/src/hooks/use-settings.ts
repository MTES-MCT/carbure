import { EntitySelection } from "./helpers/use-entity"
import use2BSCertificates from "./settings/use-2bs-certificates"
import useCompany from "./settings/use-company"
import useDeliverySites from "./settings/use-delivery-sites"
import useISCCCertificates from "./settings/use-iscc-certificates"
import useProductionSites from "./settings/use-production-sites"
import { SettingsGetter } from "./use-app"

export default function useSettings(
  entity: EntitySelection,
  settings: SettingsGetter
) {
  const company = useCompany(entity, settings)
  const productionSites = useProductionSites(entity)
  const deliverySites = useDeliverySites(entity)
  const dbsCertificates = use2BSCertificates(entity)
  const isccCertificates = useISCCCertificates(entity)

  return {
    productionSites,
    deliverySites,
    dbsCertificates,
    isccCertificates,
    company,
  }
}
