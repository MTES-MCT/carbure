import { Divider } from "common/components/divider"
import { ElecChargePointsApplicationDetails } from "elec/types"
import SampleSummary from "../sample/details-sample-summary"
import ChargePointsSampleMap from "../sample/sample-map"
import ApplicationSummary from "./details-application-summary"

interface ChargePointsApplicationHistoryProps {
  chargePointApplication: ElecChargePointsApplicationDetails | undefined
}
export const ChargePointsApplicationHistory = ({
  chargePointApplication,
}: ChargePointsApplicationHistoryProps) => {
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
            <ChargePointsSampleMap
              chargePoints={chargePointApplication?.sample?.charge_points}
            />
          </section>
        )}
      </main>
    </>
  )
}

export default ChargePointsApplicationHistory
