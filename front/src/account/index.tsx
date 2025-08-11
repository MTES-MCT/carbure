import { useTranslation } from "react-i18next"
import { Content, Main } from "common/components/scaffold"
import { AccountAccesRights } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication/authentication"
import useTitle from "common/hooks/title"
import { Navigate, Route, Routes } from "react-router-dom"
import { ROUTE_URLS } from "common/utils/routes"
import { usePrivateNavigation } from "common/layouts/navigation"
import { Tabs } from "common/components/tabs2"

const Account = () => {
  const { t } = useTranslation()

  useTitle(t("Mon compte"))
  usePrivateNavigation(t("Mon compte"))

  return (
    <Main>
      <Tabs
        tabs={[
          {
            key: "access",
            label: t("Accès aux sociétés"),
            path: ROUTE_URLS.MY_ACCOUNT.COMPANIES,
            icon: "ri-profile-line",
            iconActive: "ri-profile-fill",
          },
          {
            key: "identifiers",
            label: t("Identifiants"),
            path: ROUTE_URLS.MY_ACCOUNT.IDENTIFIERS,
            icon: "ri-settings-2-line",
            iconActive: "ri-settings-2-fill",
          },
        ]}
      />
      <Content>
        <Routes>
          <Route path="identifiers" element={<AccountAuthentication />} />
          <Route path="companies/*" element={<AccountAccesRights />} />
          <Route
            path="*"
            element={<Navigate to={ROUTE_URLS.MY_ACCOUNT.COMPANIES} />}
          />
        </Routes>
      </Content>
    </Main>
  )
}

export default Account
