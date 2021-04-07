import React, { useEffect } from "react"
import { useParams } from "react-router-dom"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"

import { Main, Title } from "common/components"
import { Return } from "common/components/icons"
import Sticky from "common/components/sticky"
import { Button } from "common/components/button"
import { SettingsBody, SettingsHeader } from "settings/components/common"
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
import { EntityType, ProductionSiteDetails } from "common/types"
import {
  ProductionSitePrompt,
  ProductionSiteState,
} from "settings/components/production-site"
import Certificates from "entities/components/certificates"

const EntityDetails = () => {
  const close = useClose("..")
  const { id } = useParams<{ id: string }>()
  const [entity, getEntity] = useAPI(api.getEntityDetails)
  const [depots, getDepots] = useAPI(api.getEntityDepots)
  const [productionSites, getProductionSites] = useAPI(api.getEntityProductionSites) // prettier-ignore
  const [certificates, getCertificates] = useAPI(api.getEntityCertificates)

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
    const entityID = parseInt(id, 10)
    getEntity(entityID)
    getDepots(entityID)
    getProductionSites(entityID)
    getCertificates(entityID)
  }, [getEntity, getDepots, getProductionSites, getCertificates, id])

  return (
    <Main>
      <SettingsHeader row>
        <Title>{entity.data?.name}</Title>
        <Button icon={Return} onClick={close}>
          Retour
        </Button>
      </SettingsHeader>

      <Sticky>
        <a href="#users">Utilisateurs</a>
        <a href="#depot">Dépots</a>
        {isProducer && <a href="#production">Sites de production</a>}
        <a href="#iscc">Certificats ISCC</a>
        <a href="#2bs">Certificats 2BS</a>
        <a href="#red">Certificats REDCert</a>
        <a href="#csn">Certificats système national</a>
      </Sticky>

      <SettingsBody>
        <UserRights />
        <DeliverySitesSettings settings={depotSettings} />
        {isProducer && (
          <ProductionSitesSettings settings={productionSiteSettings} />
        )}
        <Certificates certificates={certificates} />
      </SettingsBody>
    </Main>
  )
}

export default EntityDetails
