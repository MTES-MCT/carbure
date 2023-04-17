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
import CompanyInfo from "settings/components/company-info"
import { useTranslation } from "react-i18next"

const EntityDetails = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const { id = "" } = useParams<"id">()
  const company_id = parseInt(id, 10)
  const { t } = useTranslation()

  const company = useQuery(api.getCompanyDetails, {
    key: "entity-details",
    params: [entity.id, company_id],
  })

  const getDepots = (company_id: number) => {
    return api.getCompanyDepots(entity.id, company_id)
  }

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
          { key: "users", path: "#users", label: t("Utilisateurs") },
          {
            path: "#info",
            key: "info",
            label: t("Informations"),
          },
          !isAirline && { key: "depot", path: "#depot", label: "Depots" },
          isProducer && { key: "production", path: "#production", label: t("Sites de production") }, // prettier-ignore
          !isAirline && {
            key: "certificates",
            path: "#certificates",
            label: t("Certificats"),
          },
        ])}
      />

      <section>
        <UserRights />
        {entityData && <CompanyInfo defaultEntity={entityData} />}
        {entityData && !isAirline && (
          <DeliverySitesSettings
            readOnly
            entity={entityData}
            getDepots={getDepots}
          />
        )}
        {entityData && isProducer && (
          <ProductionSitesSettings
            readOnly
            entity={entityData}
            getProductionSites={(company_id) =>
              api.getCompanyProductionSites(entity.id, company_id)
            }
          />
        )}
        {!isAirline && <Certificates entity_id={company_id} />}
      </section>
    </Main>
  )
}

export default EntityDetails
