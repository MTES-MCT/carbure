
import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import {
  Return
} from "common/components/icons"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { ApplicationInfo } from "../../double-counting-admin/components/applications/application-info"
import ApplicationStatus from "../../double-counting-admin/components/applications/application-status"
import ApplicationTabs from "../../double-counting-admin/components/applications/application-tabs"
import { DoubleCountingStatus as DCStatus } from "../../double-counting-admin/types"
import * as api from "../api"


export const ApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const match = useHashMatch("double-counting/applications/:id")


  const applicationResponse = useQuery(api.getDoubleCountingApplicationDetails, {
    key: "dc-application",
    params: [entity.id, parseInt(match?.params.id!)],
  })


  const application = applicationResponse.result?.data.data
  const dcaStatus = application?.status ?? DCStatus.Pending


  const closeDialog = () => {
    navigate({ search: location.search, hash: "#double-counting" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog fullscreen onClose={closeDialog}>
        <header>
          <ApplicationStatus big status={dcaStatus} />
          <h1>{t("Demande d'agrément double comptage")} </h1>
        </header>

        <main>

          <ApplicationInfo application={application} />

          {application &&
            <ApplicationTabs
              productionSite={application.production_site}
              sourcing={application.sourcing}
              production={application.production}
            />
          }
        </main>

        <footer>


          <Button icon={Return} action={closeDialog}>
            <Trans>Retour</Trans>
          </Button>
        </footer>

        {applicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

