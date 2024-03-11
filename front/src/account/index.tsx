import { Trans, useTranslation } from "react-i18next"
import { Main } from "common/components/scaffold"
import { AccountAccesRights } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"
import useTitle from "common/hooks/title"
import { CompanyRegistrationDialog } from "companies/components/registration-dialog"
import { Route, Routes } from "react-router-dom"

const Account = () => {
  const { t } = useTranslation()
  useTitle(t("Mon compte"))

  return (
    <Main>
      <header>
        <h1>
          <Trans>Mon compte</Trans>
        </h1>
      </header>

      <section>
        <AccountAccesRights />
      </section>

      <section>
        <AccountAuthentication />
      </section>

      {/* <Routes>
        <Route
          path="company-registration"
          element={
            <CompanyRegistrationDialog />
          }
        />
      </Routes> */}
    </Main>
  )
}

export default Account
