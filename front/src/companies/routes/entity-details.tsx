import { useNavigate, useParams } from "react-router-dom"
import { ChevronLeft } from "common/components/icons"
import { Button } from "common/components/button"
import UserRights from "../components/user-rights"
import * as api from "../api"
import DeliverySitesSettings from "settings/components/delivery-site"
import ProductionSitesSettings from "settings/components/production-site"
import { EntityType } from "carbure/types"
import Certificates from "companies/components/certificates"
import { Main, Row } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { useQuery } from "common/hooks/async"

const EntityDetails = () => {
  const navigate = useNavigate()
  const { id = "" } = useParams<"id">()
  const entityID = parseInt(id, 10)

  const entity = useQuery(api.getEntityDetails, {
    key: "entity-details",
    params: [entityID],
  })

  const entityData = entity.result?.data.data
  const isProducer = entityData?.entity_type === EntityType.Producer

  return (
    <Main>
      <header>
        <Row style={{ alignItems: "center", gap: "var(--spacing-m)" }}>
          <Button
            icon={ChevronLeft}
            action={() => navigate("..")}
            label="Retour"
          />
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
        {entityData && isProducer && (
          <ProductionSitesSettings
            readOnly
            entity={entityData}
            getProductionSites={api.getEntityProductionSites}
          />
        )}
        <Certificates entity={entityID} />
      </section>
    </Main>
  )
}

export default EntityDetails