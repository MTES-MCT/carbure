import { ProductionSiteDetails } from "common/types"
import { Tabs } from "common/components/tabs2"
import { compact } from "common/utils/collection"
import {
  DoubleCountingProduction,
  DoubleCountingSourcing,
  DoubleCountingApplicationDetails,
} from "double-counting/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { SourcingFullTable } from "../../sourcing-table"
import { ProductionTable } from "../../production-table"
import { ProductionSiteRecap } from "./production-site-recap"
import { FilesTable } from "../../files-table"
import { Box } from "common/components/scaffold"

interface ApplicationDetailsProps {
  production?: DoubleCountingProduction[]
  sourcing?: DoubleCountingSourcing[]
  quotas?: Record<string, number>
  setQuotas?: (quotas: Record<string, number>) => void
  hasAgreement?: boolean
  productionSite?: ProductionSiteDetails
  application?: DoubleCountingApplicationDetails
}

const ApplicationTabs = ({
  productionSite,
  production,
  sourcing,
  quotas,
  setQuotas,
  hasAgreement,
  application,
}: ApplicationDetailsProps) => {
  const [focus, setFocus] = useState(
    productionSite ? "production_site" : "sourcing_forecast"
  )
  const { t } = useTranslation()

  return (
    <>
      <Tabs
        tabs={compact([
          productionSite && {
            key: "production_site",
            label: t("Site de production"),
            icon: "ri-building-line",
            iconActive: "ri-building-fill",
          },
          {
            key: "sourcing_forecast",
            label: t("Approvisionnement"),
            icon: "ri-profile-line",
            iconActive: "ri-profile-fill",
          },
          {
            key: "production",
            label: t("Production"),
            icon: "ri-user-line",
            iconActive: "ri-user-fill",
          },
          {
            key: "fichiers",
            label: t("Fichiers"),
            icon: "ri-file-line",
            iconActive: "ri-file-fill",
          },
        ])}
        focus={focus}
        onFocus={setFocus}
        sticky
      />
      {focus === "production_site" && productionSite && (
        <Box>
          <ProductionSiteRecap productionSite={productionSite} />
        </Box>
      )}

      {focus === "sourcing_forecast" && (
        <SourcingFullTable sourcing={sourcing ?? []} />
      )}

      {focus === "production" && (
        <ProductionTable
          production={production ?? []}
          quotas={quotas ?? {}}
          setQuotas={setQuotas}
          hasAgreement={hasAgreement}
          sourcing={sourcing ?? []}
        />
      )}
      {focus === "fichiers" && application && (
        <section>
          <FilesTable application={application} />
        </section>
      )}
    </>
  )
}
export default ApplicationTabs
