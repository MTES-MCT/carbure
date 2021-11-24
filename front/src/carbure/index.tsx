import { Trans, useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"

import { AppHook, useApp } from "./hooks/use-app"
import { ExternalAdminPages } from "common/types"
import useUser, { useUserContext, UserContext } from "./hooks/user"
import useEntity from "./hooks/entity"
import { UserRightProvider } from "./hooks/use-rights"

import { LoaderOverlay } from "common/components"
import Topbar from "./components/top-bar"
import Footer from "./components/footer"
import Pending from "./components/pending"
import Exit from "./components/exit"
import Registry from "./components/registry"

import TransactionsV2 from "transactions-v2"
import Settings from "settings"
import Account from "account"
import DoubleCounting from "doublecount"
import Entities from "../entities" // not using  path prevents import
import EntityDetails from "../entities/routes/entity-details"
import Dashboard from "dashboard"
import PublicStats from "./components/public-stats"
import Home from "./components/home"

const DevBanner = () => (
  <div
    style={{
      backgroundColor: "var(--orange-medium)",
      padding: "8px var(--main-spacing)",
    }}
  >
    <Trans>
      <b>Version de développement de CarbuRe :</b> les manipulations effectuées
      ici n'ont pas de répercussion et les déclarations ne sont pas prises en
      compte.
    </Trans>
  </div>
)

// has to be nested in a route so we can get data from useParams()
const Org = ({ app }: { app: AppHook }) => {
  const entity = useEntity()
  const user = useUserContext()

  if (!user.isAuthenticated()) {
    return <Exit to="/accounts/login" />
  }

  const { isAdmin } = entity

  return (
    <UserRightProvider app={app}>
      <Routes>
        <Route path="transactions-v2/*" element={<TransactionsV2 />} />

        <Route path="settings" element={<Settings settings={app.settings} />} />
        <Route path="registry" element={<Registry />} />

        {isAdmin && <Route path="dashboard" element={<Dashboard />} />}
        {isAdmin && <Route path="entities" element={<Entities />} />}
        {isAdmin && <Route path="entities/:id" element={<EntityDetails />} />}

        {(isAdmin || entity.hasPage(ExternalAdminPages.DoubleCounting)) && (
          <Route path="double-counting/*" element={<DoubleCounting />} />
        )}

        <Route path="*" element={<Navigate to="transactions-v2" />} />
      </Routes>

      {user.loading && <LoaderOverlay />}
    </UserRightProvider>
  )
}

const Carbure = () => {
  useTranslation()

  const app = useApp()
  const user = useUser()

  return (
    <UserContext.Provider value={user}>
      <div id="app">
        {!app.isProduction() && <DevBanner />}

        <Topbar />

        <Routes>
          <Route path="/" element={<Home app={app} />} />
          <Route path="/pending" element={<Pending />} />
          <Route path="/logout" element={<Exit to="/accounts/logout" />} />
          <Route path="/account" element={<Account app={app} />} />
          <Route path="/org/:entity/*" element={<Org app={app} />} />
          <Route path="/public_stats" element={<PublicStats />} />
        </Routes>

        <Footer />
      </div>
    </UserContext.Provider>
  )
}

export default Carbure
