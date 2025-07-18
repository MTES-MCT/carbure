import useEntity from "common/hooks/entity"
import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { ApplicationInfo } from "double-counting-admin/components/applications/application-info"
import ApplicationStatus from "./application-status"
import { DoubleCountingStatus as DCStatus } from "double-counting/types"
import * as api from "double-counting/api"
import { formatDateYear } from "common/utils/formatters"
import ApplicationTabs from "./applications/application-tabs"
import { compact } from "common/utils/collection"
import { DechetIndustrielAlert } from "./application-checker/industrial-waste-alert"

export const ApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const match = useHashMatch("double-counting/applications/:id")
  const applicationID = parseInt(match?.params.id || "")

  const applicationResponse = useQuery(
    api.getDoubleCountingApplicationDetails,
    {
      key: "dc-application",
      params: [entity.id, applicationID],
    }
  )

  const uploadFiles = useMutation(api.uploadDoubleCountingApplicationFiles, {
    invalidates: ["dc-application"],
  })

  const deleteFile = useMutation(api.deleteDoubleCountingApplicationFile, {
    invalidates: ["dc-application"],
  })

  const application = applicationResponse.result?.data
  const dcaStatus = application?.status ?? DCStatus.PENDING
  const isPending = dcaStatus === DCStatus.PENDING
  const period = application?.period_start
    ? `${formatDateYear(application.period_start)}-${formatDateYear(application.period_end)}`
    : "N/A"

  const isPendingFiles =
    application?.has_dechets_industriels && application.documents.length <= 1

  const files = application?.documents ?? []
  const loading =
    applicationResponse.loading || uploadFiles.loading || deleteFile.loading

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#double-counting" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        fullscreen
        onClose={closeDialog}
        gap="lg"
        header={
          <>
            <Dialog.Title style={{ justifyContent: "space-between" }}>
              {t("Demande d'agrément double comptage")}
              <ApplicationStatus status={dcaStatus} />
            </Dialog.Title>
            <Dialog.Description>
              <ApplicationInfo application={application} />
            </Dialog.Description>
          </>
        }
      >
        <p>
          <Trans
            values={{ period }}
            defaults="Période de validité : <b>{{ period }}</b>"
          />
        </p>

        {isPendingFiles && <DechetIndustrielAlert />}

        {application && (
          <ApplicationTabs
            readOnly={!isPending}
            productionSite={application.production_site}
            sourcing={application.sourcing}
            production={application.production}
            files={files}
            onAddFiles={(files) => {
              const extra_files = compact(files.map((f) => f.file))
              uploadFiles.execute(entity.id, application.id, extra_files)
            }}
            onDeleteFile={(file) => {
              deleteFile.execute(entity.id, application.id, file.id)
            }}
          />
        )}

        {loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}
