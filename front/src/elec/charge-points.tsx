import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import * as api from "./api-charge-points"
import { ChargePointsTabs } from "./charge-points-tabs"
import { ChargePointsSnapshot } from "./types-charge-points"

const defaultSnapshot: ChargePointsSnapshot = {
  charge_points: 0,
  charge_points_pending: 0,
  meter_reading: 0,
}

const ChargePoints = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const years = useYears("charge-points", api.getYears)
  const snapshotResponse = useQuery(api.getChargePointsSnapshot, {
    key: "charge-points-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot = snapshotResponse.result?.data.data ?? defaultSnapshot

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Points de recharge")}</h1>

          <Select
            loading={years.loading}
            variant="inline"
            placeholder={t("Choisir une année")}
            value={years.selected}
            onChange={years.setYear}
            options={years.options}
            sort={(year) => -year.value}
          />
        </section>

        <section>
          <ChargePointsTabs
            loading={snapshotResponse.loading}
            snapshot={snapshot}
          />
        </section>
      </header>
    </Main>
  )
}

export default ChargePoints
