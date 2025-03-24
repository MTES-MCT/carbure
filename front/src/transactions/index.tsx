import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import HashRoute from "common/components/hash-route"
import { UserRole } from "common/types"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import * as api from "./api"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { DeclarationButton, DeclarationDialog } from "./actions/declaration"
import { ImportArea } from "./actions/import"
import Lots from "./components/lots"
import Stocks from "./components/stocks"
import useYears from "common/hooks/years"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("transactions", api.getYears)

  const snapshot = useQuery(api.getSnapshot, {
    key: "snapshot",
    params: [entity.id, years.selected],
  })

  const snapshotData = snapshot.result?.data.data

  // common props for subroutes
  const props = { year: years.selected, snapshot: snapshotData }

  return (
    <ImportArea>
      <Main>
        <header>
          <section>
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
