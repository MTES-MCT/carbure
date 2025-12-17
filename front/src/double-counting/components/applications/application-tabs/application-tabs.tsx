import { ProductionSiteDetails } from "common/types"
import { Tabs } from "common/components/tabs2"
import { compact } from "common/utils/collection"
import {
  DoubleCountingProduction,
  DoubleCountingSourcing,
  DoubleCountingFile,
} from "double-counting/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { SourcingFullTable } from "../../sourcing-table"
import { ProductionTable } from "../../production-table"
import { ProductionSiteRecap } from "./production-site-recap"
import { Box } from "common/components/scaffold"
import { FilesManager } from "double-counting/components/files-manager"

interface ApplicationDetailsProps {
  readOnly?: boolean
  production?: DoubleCountingProduction[]
  sourcing?: DoubleCountingSourcing[]
  quotas?: Record<string, number>
  setQuotas?: (quotas: Record<string, number>) => void
  hasAgreement?: boolean
  productionSite?: ProductionSiteDetails
  files?: DoubleCountingFile[]
  onAddFiles?: (files: DoubleCountingFile[]) => void
  onDeleteFile?: (file: DoubleCountingFile) => void
  applicationId?: number
  entityId?: number
}

const ApplicationTabs = ({
  readOnly,
  productionSite,
  production,
  sourcing,
  quotas,
  setQuotas,
  hasAgreement,
  files,
  onAddFiles,
  onDeleteFile,
  applicationId,
  entityId,
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

      {focus === "fichiers" && (
        <FilesManager
          readOnly={readOnly}
          files={files}
          onAddFiles={onAddFiles}
          onDeleteFile={onDeleteFile}
          applicationId={applicationId}
          entityId={entityId}
        />
      )}
    </>
  )
}
export default ApplicationTabs
