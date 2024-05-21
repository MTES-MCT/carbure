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
import * as api from "elec-audit/api"
import { Divider } from "common/components/divider"
import SampleSummary from "elec-audit-admin/components/charge-points/details-sample-summary"
import ChargePointsSampleMap from "elec-audit-admin/components/charge-points/sample-map"
import Button from "common/components/button"
import { Download } from "common/components/icons"
import ApplicationSummary from "./details-application-summary"



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


  const downloadSample = async () => {
    return api.downloadChargePointsSample(entity.id, chargePointApplication!.id)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} >
        <header>
          <ApplicationStatus status={chargePointApplication?.status} big />
          <h1>{t("Inscription de points de recharge")}</h1>
        </header>

        <main>
          <section>
            <ApplicationSummary application={chargePointApplication} />
          </section>
          <Divider />
          {chargePointApplication?.sample && (
            <section>
              <ChargePointsSampleMap chargePoints={chargePointApplication?.sample?.charge_points} />
            </section>
          )}

        </main>

        <footer>
          <Button icon={Download} label={t("Télécharger le retour de contrôle")} variant="secondary" action={downloadSample} style={{ width: "min-content" }} />

        </footer>
        {chargePointApplicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal >
  )
}




export default ChargingPointsApplicationDetailsDialog
