import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Routes } from "react-router-dom"
import { ImportArea } from "../transactions/actions/import"
import * as api from "./api"
import ClientTabs from "./components/client-tabs"
import { safClientSnapshot } from "./__test__/data"

export const SafClient = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("saf", api.getYears)

  const snapshot = useQuery(api.getSafSnapshot, {
    key: "snapshot",
    params: [entity.id, years.selected],
  })
  // const snapshotData = snapshot.result?.data.data
  const snapshotData = safClientSnapshot //TO TEST with testing data

  return (
    <ImportArea>
      <Main>
        <header>
          <section>
            <h1>{t("Carburant Durable d’Aviation - CDA")}</h1>

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
            <ClientTabs loading={snapshot.loading} count={snapshotData} />
          </section>
        </header>

        <Routes></Routes>
      </Main>
    </ImportArea>
  )
}

export default SafClient
