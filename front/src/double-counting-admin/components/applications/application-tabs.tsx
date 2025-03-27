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
import { ProductionSiteForm } from "settings/components/production-site-dialog"
import { SourcingFullTable } from "../../../double-counting/components/sourcing-table"
import { ProductionTable } from "../../../double-counting/components/production-table"
import { FilesTable } from "../../../double-counting/components/files-table"
import { Box } from "common/components/scaffold"
import {
  BuildingFill,
  BuildingLine,
  ProfileFill,
  ProfileLine,
  UserFill,
  UserLine,
} from "common/components/icon"

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
            icon: BuildingLine,
            iconActive: BuildingFill,
          },
          {
            key: "sourcing_forecast",
            label: t("Approvisionnement"),
            icon: ProfileLine,
            iconActive: ProfileFill,
          },
          {
            key: "production",
            label: t("Production"),
            icon: UserLine,
            iconActive: UserFill,
          },
          {
            key: "fichiers",
            label: t("Fichiers"),
          },
        ])}
        focus={focus}
        onFocus={setFocus}
      />
      {focus === "production_site" && productionSite && (
        <Box>
          <ProductionSiteForm readOnly productionSite={productionSite} />
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
