import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import HashRoute from "common/components/hash-route"
import { UserRole } from "carbure/types"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import * as api from "./api"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import StatusTabs from "./components/status"
import { DeclarationButton, DeclarationDialog } from "./actions/declaration"
import { ImportArea } from "./actions/import"
import Lots from "./components/lots"
import Stocks from "./components/stocks"
import useYears from "common/hooks/years-2"
import { apiTypes } from "common/services/api-fetch.types"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("transactions", api.getYears)

  const snapshot = useQuery(api.getSnapshot, {
    key: "snapshot",
    params: [entity.id, years.selected],
  })

  // Endpoint returns a different type if we are admin or not
  // In our case, this is not an admin page, so we can safely cast to the expected type
  const snapshotData = snapshot.result?.data as apiTypes["SnapshotReponse"]

  // common props for subroutes
  const props = { year: years.selected, snapshot: snapshotData }

  return (
    <ImportArea>
      <Main>
        <header>
          <section>
            <h1>{t("Transactions")}</h1>

            <Select
              loading={years.loading}
              variant="inline"
              placeholder={t("Choisir une année")}
              value={years.selected}
              onChange={years.setYear}
              options={years.options}
              sort={(year) => -year.value}
            />

            {entity.hasRights(UserRole.Admin, UserRole.ReadWrite) && (
              <DeclarationButton />
            )}
          </section>

          <section>
            <StatusTabs loading={snapshot.loading} count={snapshotData} />
          </section>
        </header>

        <Routes>
          <Route
            path="stocks/*"
            element={
              // if entity does not have stock redirect to default drafts
              entity.has_stocks ? (
                <Stocks {...props} />
              ) : (
                <Navigate replace to="../drafts/imported" />
              )
            }
          />
          <Route path="*" element={<Lots {...props} />} />
        </Routes>

        <HashRoute path="declaration/*" element={<DeclarationDialog />} />
      </Main>
    </ImportArea>
  )
}

export default Transactions
