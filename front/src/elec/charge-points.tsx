import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import * as api from "./api-charge-points"
import { ChargePointsTabs } from "./charge-points-tabs"

const ChargePoints = () => {
  const { t } = useTranslation()
  const years = useYears("charge-points", api.getYears)

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
          <ChargePointsTabs />
        </section>
      </header>
    </Main>
  )
}

export default ChargePoints
