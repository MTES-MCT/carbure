import useEntity from "common/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useMutation, useQuery } from "common/hooks/async"
import * as apiCpo from "elec/api-cpo"
import ChargePointsApplicationsTable from "elec/components/charge-points/table"
import ElecChargePointsFileUpload from "./upload-dialog"
import { ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"
import { deleteChargePointsApplication } from "./api"
import { usePrivateNavigation } from "common/layouts/navigation"

const ChargePointsApplications = () => {
  const entity = useEntity()
  const { t } = useTranslation()
  usePrivateNavigation(t("Inscription"))
  const portal = usePortal()

  const applicationsResponse = useQuery(apiCpo.getChargePointsApplications, {
    key: "charge-points-applications",
    params: [entity.id, entity.id],
  })

  const deleteApplication = useMutation(
    (id: number) => deleteChargePointsApplication(entity.id, id),
    { invalidates: ["charge-points-applications"] }
  )

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
    <section>
      <Button
        asideX={true}
        variant="primary"
        icon={Plus}
        action={showUploadDialog}
        label={t("Inscrire des points de recharge")}
      />

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
          onDeleteChargePointsApplication={deleteApplication.execute}
        />
      )}
    </section>
  )
}

export default ChargePointsApplications
