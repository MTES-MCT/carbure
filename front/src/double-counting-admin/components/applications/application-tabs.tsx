import { ProductionSiteDetails } from "common/types"
import Tabs from "common/components/tabs"
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
      <section>
        <Tabs
          variant="switcher"
          tabs={compact([
            productionSite && {
              key: "production_site",
              label: t("Site de production"),
            },
            {
              key: "sourcing_forecast",
              label: t("Approvisionnement"),
            },
            {
              key: "production",
              label: t("Production"),
            },
            {
              key: "fichiers",
              label: t("Fichiers"),
            },
          ])}
          focus={focus}
          onFocus={setFocus}
        />
      </section>
      {focus === "production_site" && productionSite && (
        <section>
          <ProductionSiteForm readOnly productionSite={productionSite} />
        </section>
      )}

      {focus === "sourcing_forecast" && (
        <section>
          <SourcingFullTable sourcing={sourcing ?? []} />
        </section>
      )}

      {focus === "production" && (
        <section>
          <ProductionTable
            production={production ?? []}
            quotas={quotas ?? {}}
            setQuotas={setQuotas}
            hasAgreement={hasAgreement}
            sourcing={sourcing ?? []}
          />
        </section>
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
