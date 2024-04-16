import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import * as api from "elec-admin/api"
import { ElecMeterReadingsApplication } from "elec/types"
import { Trans, useTranslation } from "react-i18next"

import MeterReadingsApplicationsTable from "./table"


const ElecAdminMeterReadingsSettings = ({ companyId }: { companyId: number }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  const applicationsQuery = useQuery(api.getMeterReadingsApplications, {
    key: "meter-readings-applications",
    params: [entity.id, companyId],
  })

  const applications = applicationsQuery.result?.data.data ?? []
  // const applications = elecMeterReadingsApplications
  const isEmpty = applications.length === 0




  const downloadMeterReadingsApplication = (application: ElecMeterReadingsApplication) => {
    return api.downloadMeterReadingsApplicationDetails(entity.id, companyId, application.id)
  }

  return (
    <Panel id="elec-meter-readings">
      <header>
        <h1>
          {t("Relevés trimestriels")}
        </h1>
      </header>



      {isEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun relevé trimestriel trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isEmpty && (
        <>
          <MeterReadingsApplicationsTable
            applications={applications}
            onDownloadMeterReadingsApplication={downloadMeterReadingsApplication}
          />
        </>


      )}

      {applicationsQuery.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default ElecAdminMeterReadingsSettings
