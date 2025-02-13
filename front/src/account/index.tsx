import { useTranslation } from "react-i18next"
import { Main } from "common/components/scaffold"
import { AccountAccesRights, EntityDialog } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"
import useTitle from "common/hooks/title"
import { CompanyRegistrationDialog } from "companies/components/registration-dialog"
import { Route, Routes, useNavigate } from "react-router-dom"
import { ROUTE_URLS } from "common/utils/routes"
import { usePrivateNavigation } from "common/layouts/navigation"

const Account = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  useTitle(t("Mon compte"))
  usePrivateNavigation(t("Mon compte"))

  return (
    <Main>
      <Routes>
        <Route
          path="add-company"
          element={
            <EntityDialog
              onClose={() => navigate(ROUTE_URLS.MY_ACCOUNT.INDEX)}
            />
          }
        />
        <Route
          path="company-registration"
          element={<CompanyRegistrationDialog />}
        />
      </Routes>
      <section>
        <AccountAccesRights />
      </section>

      <section>
        <AccountAuthentication />
      </section>
    </Main>
  )
}

export default Account
