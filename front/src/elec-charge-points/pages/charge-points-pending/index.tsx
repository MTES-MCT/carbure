import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useQuery } from "common/hooks/async"
import * as apiCpo from "elec/api-cpo"
import ChargePointsApplicationsTable from "elec/components/charge-points/table"
import ElecChargePointsFileUpload from "./upload-dialog"
import { ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"

type ChargePointsPendingProps = {
  year: number
}

const ChargePointsPending = ({ year }: ChargePointsPendingProps) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const portal = usePortal()

  const applicationsResponse = useQuery(apiCpo.getChargePointsApplications, {
    key: "charge-points-applications",
    params: [entity.id, entity.id, year],
  })

  const applications = applicationsResponse.result?.data.data ?? []

  const downloadChargePointsApplication = (
    application: ElecChargePointsApplication
  ) => {
    return apiCpo.downloadChargePointsApplicationDetails(
      entity.id,
      application.id
    )
  }

  const showUploadDialog = () => {
    portal((resolve) => <ElecChargePointsFileUpload onClose={resolve} />)
  }

  return (
    <>
      <section>
        <Button
          asideX={true}
          variant="primary"
          icon={Plus}
          action={showUploadDialog}
          label={t("Inscrire des points de recharge")}
        />
      </section>

      {applications.length === 0 ? (
        <section>
          <Alert icon={AlertCircle} variant="warning">
            {t("Aucun point de recharge trouvé")}
          </Alert>
        </section>
      ) : (
        <ChargePointsApplicationsTable
          applications={applications}
          onDownloadChargePointsApplication={downloadChargePointsApplication}
        />
      )}
    </>
  )
}

export default ChargePointsPending
