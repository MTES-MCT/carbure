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
import useEntity from "carbure/hooks/entity"

const EntityDetails = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const { id = "" } = useParams<"id">()
  const companyID = parseInt(id, 10)

  const company = useQuery(api.getEntityDetails, {
    key: "entity-details",
    params: [entity.id, companyID],
  })

  const entityData = company.result?.data.data
  const isProducer = entityData?.entity_type === EntityType.Producer
  const isAirline = entityData?.entity_type === EntityType.Airline

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
          !isAirline && { key: "depot", path: "#depot", label: "Depots" },
          isProducer && { key: "production", path: "#production", label: "Sites de production" }, // prettier-ignore
          !isAirline && {
            key: "certificates",
            path: "#certificates",
            label: "Certificats",
          },
        ])}
      />

      <section>
        <UserRights />
        {entityData && !isAirline && (
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
        {!isAirline && <Certificates entity={companyID} />}
      </section>
    </Main>
  )
}

export default EntityDetails
