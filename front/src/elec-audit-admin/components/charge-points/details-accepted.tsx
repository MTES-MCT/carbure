import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { Check, Cross, Download } from "common/components/icons"
import { ElecChargePointsApplicationDetails } from "elec/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import ApplicationSummary from "./details-application-summary"
import SampleSummary from "../sample/details-sample-summary"
import ChargePointsSampleMap from "../sample/sample-map"




interface ChargingPointsApplicationDetailsAcceptedProps {
  chargePointApplication: ElecChargePointsApplicationDetails | undefined

}
export const ChargingPointsApplicationDetailsAccepted = ({
  chargePointApplication,
}: ChargingPointsApplicationDetailsAcceptedProps) => {
  const { t } = useTranslation()
  const [confirmCheckbox, setConfirmCheckbox] = useState(false)

  return (
    <>
      <main>
        <section>
          <ApplicationSummary application={chargePointApplication} />
        </section>
        <Divider />
        {chargePointApplication?.sample && (
          <section>
            <SampleSummary sample={chargePointApplication?.sample} />
            <ChargePointsSampleMap chargePoints={chargePointApplication?.sample?.charge_points} />
          </section>
        )}

      </main>
    </>
  )
}


export default ChargingPointsApplicationDetailsAccepted
