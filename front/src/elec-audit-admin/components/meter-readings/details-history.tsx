import { Divider } from "common/components/divider"
import { ElecMeterReadingsApplicationDetails } from "elec/types"
import SampleSummary from "../sample/details-sample-summary"
import ChargePointsSampleMap from "../sample/sample-map"
import ApplicationSummary from "./details-application-summary"




interface MeterReadingsApplicationHistoryProps {
  meterReadingsApplication: ElecMeterReadingsApplicationDetails | undefined

}
export const MeterReadingsApplicationHistory = ({
  meterReadingsApplication,
}: MeterReadingsApplicationHistoryProps) => {

  return (
    <>
      <main>
        <section>
          <ApplicationSummary application={meterReadingsApplication} />
        </section>
        <Divider />
        {meterReadingsApplication?.sample && (
          <section>
            <SampleSummary sample={meterReadingsApplication?.sample} />
            <ChargePointsSampleMap chargePoints={meterReadingsApplication?.sample?.charge_points} />
          </section>
        )}

      </main>
    </>
  )
}


export default MeterReadingsApplicationHistory
