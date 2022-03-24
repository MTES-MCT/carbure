import { useEffect } from "react"
import { useParams } from "react-router-dom"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"

import { ChevronLeft, Return } from "common-v2/components/icons"
import { Button } from "common-v2/components/button"
import UserRights from "../components/user-rights"
import * as api from "../api"
import DeliverySitesSettings, {
  DeliverySitePrompt,
} from "settings/components/delivery-site"
import {
  DeliverySiteSettingsHook,
  EntityDeliverySite,
} from "settings/hooks/use-delivery-sites"
import { ProductionSiteSettingsHook } from "settings/hooks/use-production-sites"
import ProductionSitesSettings from "settings/components/production-site"
import { prompt } from "common/components/dialog"
import { EntityType } from "carbure/types"
import { ProductionSiteDetails } from "common/types"
import {
  ProductionSitePrompt,
  ProductionSiteState,
} from "settings/components/production-site"
import Certificates from "entities/components/certificates"
import { Main, Row } from "common-v2/components/scaffold"
import Tabs from "common-v2/components/tabs"
import { compact } from "common-v2/utils/collection"

const EntityDetails = () => {
  const close = useClose("..")
  const { id = "" } = useParams<"id">()
  const entityID = parseInt(id, 10)

  const [entity, getEntity] = useAPI(api.getEntityDetails)
  const [depots, getDepots] = useAPI(api.getEntityDepots)
  const [productionSites, getProductionSites] = useAPI(api.getEntityProductionSites) // prettier-ignore

  const isProducer = entity.data?.entity_type === EntityType.Producer

  async function showDeliverySite(ds: EntityDeliverySite) {
    prompt((resolve) => (
      <DeliverySitePrompt
        title="Détails du dépôt"
        deliverySite={ds}
        onResolve={resolve}
      />
    ))
  }

  async function editProductionSite(ps: ProductionSiteDetails) {
    // "Détails du site de production",
    prompt<ProductionSiteState>((resolve) => (
      <ProductionSitePrompt
        readOnly
        title="Détails du site de production"
        entity={entity.data}
        productionSite={ps}
        onResolve={resolve}
      />
    ))
  }

  const depotSettings: DeliverySiteSettingsHook = {
    deliverySites: depots.data ?? [],
    isLoading: depots.loading,
    isEmpty: (depots.data ?? []).length === 0,
    showDeliverySite,
  }

  const productionSiteSettings: ProductionSiteSettingsHook = {
    productionSites: productionSites.data ?? [],
    isLoading: productionSites.loading,
    isEmpty: (productionSites.data ?? []).length === 0,
    editProductionSite,
  }

  useEffect(() => {
    getEntity(entityID)
    getDepots(entityID)
    getProductionSites(entityID)
  }, [getEntity, getDepots, getProductionSites, entityID])

  return (
    <Main>
      <header>
        <Row style={{ alignItems: "center", gap: "var(--spacing-m)" }}>
          <Button icon={ChevronLeft} action={close} label="Retour" />
          <h1>{entity.data?.name}</h1>
        </Row>
      </header>

      <Tabs
        variant="sticky"
        tabs={compact([
          { key: "users", path: "#users", label: "Utilisateurs" },
          { key: "depot", path: "#depot", label: "Depots" },
          isProducer && {
            key: "production",
            path: "#production",
            label: "Sites de production",
          },
          { key: "certificates", path: "#certificates", label: "Certificats" },
        ])}
      />

      <section>
        <UserRights />
        <DeliverySitesSettings settings={depotSettings} />
        {isProducer && (
          <ProductionSitesSettings settings={productionSiteSettings} />
        )}
        <Certificates entity={entityID} />
      </section>
    </Main>
  )
}

export default EntityDetails
