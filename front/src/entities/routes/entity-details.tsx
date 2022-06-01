import { useEffect } from "react"
import { useParams } from "react-router-dom"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"

import { ChevronLeft } from "common-v2/components/icons"
import { Button } from "common-v2/components/button"
import UserRights from "../components/user-rights"
import * as api from "../api"
import DeliverySitesSettings from "settings/components/delivery-site"
import { ProductionSiteSettingsHook } from "settings/hooks/use-production-sites"
import ProductionSitesSettings from "settings/components/production-site"
import { EntityType } from "carbure/types"
import { ProductionSiteDetails } from "common/types"
import { ProductionSitePrompt } from "settings/components/production-site"
import Certificates from "entities/components/certificates"
import { Main, Row } from "common-v2/components/scaffold"
import Tabs from "common-v2/components/tabs"
import { compact } from "common-v2/utils/collection"
import { usePortal } from "common-v2/components/portal"
import { useQuery } from "common-v2/hooks/async"

const EntityDetails = () => {
  const close = useClose("..")
  const portal = usePortal()
  const { id = "" } = useParams<"id">()
  const entityID = parseInt(id, 10)

  const entity = useQuery(api.getEntityDetails, {
    key: "entity-details",
    params: [entityID],
  })

  const productionSites = useQuery(api.getEntityProductionSites, {
    key: "production-sites",
    params: [entityID],
  })

  const entityData = entity.result?.data.data
  const isProducer = entityData?.entity_type === EntityType.Producer

  async function editProductionSite(ps: ProductionSiteDetails) {
    // "Détails du site de production",
    portal((close) => (
      <ProductionSitePrompt
        readOnly
        title="Détails du site de production"
        entity={entityData}
        productionSite={ps}
        onResolve={close}
      />
    ))
  }

  const productionSitesData = productionSites.result?.data.data

  const productionSiteSettings: ProductionSiteSettingsHook = {
    productionSites: productionSitesData ?? [],
    isLoading: productionSites.loading,
    isEmpty: (productionSitesData ?? []).length === 0,
    editProductionSite,
  }

  return (
    <Main>
      <header>
        <Row style={{ alignItems: "center", gap: "var(--spacing-m)" }}>
          <Button icon={ChevronLeft} action={close} label="Retour" />
          <h1>{entityData?.name}</h1>
        </Row>
      </header>

      <Tabs
        variant="sticky"
        tabs={compact([
          { key: "users", path: "#users", label: "Utilisateurs" },
          { key: "depot", path: "#depot", label: "Depots" },
          isProducer && { key: "production", path: "#production", label: "Sites de production" }, // prettier-ignore
          { key: "certificates", path: "#certificates", label: "Certificats" },
        ])}
      />

      <section>
        <UserRights />
        {entityData && (
          <DeliverySitesSettings
            readOnly
            entity={entityData}
            getDepots={api.getEntityDepots}
          />
        )}
        {isProducer && (
          <ProductionSitesSettings settings={productionSiteSettings} />
        )}
        <Certificates entity={entityID} />
      </section>
    </Main>
  )
}

export default EntityDetails
