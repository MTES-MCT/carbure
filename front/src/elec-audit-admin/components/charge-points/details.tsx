import useEntity from "carbure/hooks/entity"
import { Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import ApplicationStatus from "elec/components/application-status"
import { ElecAuditApplicationStatus } from "elec/types"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import ChargePointsApplicationAcceptDialog from "./accept-dialog"
import ChargingPointsApplicationDetailsPending from "./details-pending"
import ChargePointsApplicationRejectDialog from "./reject-dialog"


export const ChargingPointsApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("application/:id")

  const chargePointApplicationResponse = useQuery(api.getChargePointsApplicationDetails, {
    key: "audit-charge-points-application-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  const chargePointApplication = chargePointApplicationResponse.result?.data.data


  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const acceptApplication = (force: boolean = false) => {
    if (!chargePointApplication) return
    portal((close) => (
      <ChargePointsApplicationAcceptDialog
        application={chargePointApplication}
        onClose={close}
        forceValidation={force}
        onValidated={closeDialog}
      />
    ))
  }

  const rejectApplication = (force: boolean = false) => {
    if (!chargePointApplication) return
    portal((close) => (
      <ChargePointsApplicationRejectDialog
        application={chargePointApplication}
        onClose={close}
        forceRejection={force}
        onRejected={closeDialog}

      />
    ))
  }


  const downloadSample = async () => {
    return api.downloadChargePointsSample(entity.id, chargePointApplication!.id, true)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} >
        <header>
          <ApplicationStatus status={chargePointApplication?.status} big />

          <h1>{t("Inscription de points de recharge")}</h1>
        </header>
        {chargePointApplication?.status === ElecAuditApplicationStatus.Pending && (
          <ChargingPointsApplicationDetailsPending
            chargePointApplication={chargePointApplication}
            onAccept={acceptApplication}
            onReject={rejectApplication}
            onDownloadSample={downloadSample}
          />
        )}

        {chargePointApplicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal >
  )
}




export default ChargingPointsApplicationDetailsDialog
