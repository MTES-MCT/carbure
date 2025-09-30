import { useTranslation } from "react-i18next"
import { useNavigate, useParams } from "react-router-dom"
import { ChevronLeft } from "common/components/icons"
import { Button } from "common/components/button"
import UserRights from "../components/user-rights"
import * as api from "../api"
import DeliverySitesSettings from "settings/pages/delivery-site"
import ProductionSitesSettings from "settings/pages/production-site"
import DoubleCountingSettings from "double-counting/components/settings"
import { EntityType } from "common/types"
import Certificates from "companies-admin/components/certificates"
import { Main, Row } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import HashRoute from "common/components/hash-route"

import { compact } from "common/utils/collection"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import CompanyInfo from "settings/pages/company-info"
import { AuthorizeEntityBanner } from "companies-admin/components/authorize-entity-banner"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ExtAdminPagesEnum } from "api-schema"
import { ApplicationDetailsDialog } from "double-counting-admin/components/applications/application-details-dialog"
import { AgreementDetailsDialog } from "double-counting-admin/components/agreements/agreement-details-dialog"

const EntityDetails = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const { id = "" } = useParams<"id">()
  const companyId = parseInt(id, 10)
  const { t } = useTranslation()
  usePrivateNavigation(t("Sociétés"))

  const company = useQuery(api.getCompanyDetails, {
    key: "entity-details",
    params: [entity.id, companyId],
  })

  const getDepots = (company_id: number) => {
    return api.getCompanyDepots(entity.id, company_id)
  }

  const canWrite = entity.canWrite()

  const entityData = company.result?.data
  const isEnabled = Boolean(entityData?.is_enabled)
  const isProducer = entityData?.entity_type === EntityType.Producer
  const isAirline = entityData?.entity_type === EntityType.Airline
  const isSAFTrader = entityData?.entity_type === EntityType.SAF_Trader
  const isSAFEntity = isAirline || isSAFTrader

  const canApprove =
    entity.isAdmin ||
    entity.hasAdminRight("AIRLINE") ||
    entity.hasAdminRight("ELEC") ||
    entity.hasAdminRight(ExtAdminPagesEnum.DCA)

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
          !isSAFEntity && {
            key: "depot",
            path: "#depot",
            label: "Depots",
          },
          isProducer && {
            key: "production",
            path: "#production",
            label: t("Sites de production"),
          },
          isProducer && {
            path: "#double-counting",
            key: "double-counting",
            label: t("Double comptage"),
          },
          !isSAFEntity && {
            key: "certificates",
            path: "#certificates",
            label: t("Certificats"),
          },
        ])}
      />

      <section>
        {!isEnabled && entityData && canApprove && (
          <AuthorizeEntityBanner company={entityData} />
        )}

        <UserRights readOnly={!isEnabled || !canApprove || !canWrite} />
        {entityData && (
          <CompanyInfo readOnly company={entityData} key={entityData.id} />
        )}
        {entityData && !isSAFEntity && (
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
            getProductionSites={(companyId) =>
              api.getCompanyProductionSites(entity.id, companyId)
            }
          />
        )}
        {entityData && isProducer && (
          <DoubleCountingSettings
            readOnly={!canWrite}
            entity={entityData}
            getDoubleCountingAgreements={(companyId) =>
              api.getCompanyDoubleCountingAgreements(entity.id, companyId)
            }
          />
        )}
        {!isSAFEntity && (
          <Certificates
            readOnly={!canWrite || !isEnabled}
            entity_id={companyId}
          />
        )}
      </section>

      <HashRoute
        path="application/:id"
        element={<ApplicationDetailsDialog />}
      />
      <HashRoute
        path="agreement/:id" //
        element={<AgreementDetailsDialog />}
      />
    </Main>
  )
}

export default EntityDetails
