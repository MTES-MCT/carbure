import { Trans, useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import useUser, { useUserContext, UserContext } from "./hooks/user"
import useEntity from "./hooks/entity"
import { LoaderOverlay } from "common/components"
import Topbar from "./components/top-bar"
import Footer from "./components/footer"
import Pending from "./components/pending"
import Exit from "./components/exit"
import Registry from "./components/registry"
import PublicStats from "./components/public-stats"
import Home from "./components/home"
import Transactions from "transactions-v2"
import Settings from "settings"
import Account from "account"
import DoubleCounting from "doublecount"
import Dashboard from "dashboard"
import Entities from "../entities" // not using  path prevents import

const Carbure = () => {
  useTranslation()

  const user = useUser()

  return (
    <UserContext.Provider value={user}>
      <div id="app">
        <DevBanner />

        <Topbar />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pending" element={<Pending />} />
          <Route path="/logout" element={<Exit to="/accounts/logout" />} />
          <Route path="/account" element={<Account />} />
          <Route path="/org/:entity/*" element={<Org />} />
          <Route path="/public_stats" element={<PublicStats />} />
        </Routes>

        <Footer />
      </div>
    </UserContext.Provider>
  )
}

// has to be nested in a route so we can get data from useParams()
const Org = () => {
  const entity = useEntity()
  const user = useUserContext()

  if (!user.isAuthenticated()) {
    return <Exit to="/accounts/login" />
  }

  const { isAdmin, isAuditor, isExternal, isIndustry } = entity
  const hasDCA = isExternal && entity.hasPage("DCA")

  // prettier-ignore
  return (
    <>
      <Routes>
        <Route path="settings" element={<Settings />} />

        {isIndustry && <Route path="transactions/*" element={<Transactions />} />}
        {isIndustry && <Route path="registry" element={<Registry />} />}

        {isAdmin && <Route path="dashboard" element={<Dashboard />} />}
        {isAdmin && <Route path="entities/*" element={<Entities />} />}

        {(isAdmin || isAuditor) && <Route path="controls/*" element={<h1>TODO</h1>} />}
        {(isAdmin || hasDCA) && <Route path="double-counting/*" element={<DoubleCounting />} />}

        {isIndustry && <Route path="*" element={<Navigate to="transactions" />} />}
        {isAdmin && <Route path="*" element={<Navigate to="dashboard" />} />}
        {isAuditor && <Route path="*" element={<Navigate to="controls" />} />}
        {hasDCA && <Route path="*" element={<Navigate to="double-counting" />} />}
      </Routes>

      {user.loading && <LoaderOverlay />}
    </>
  )
}

const DevBanner = () => {
  if (window.location.hostname === "carbure.beta.gouv.fr") return null

  return (
    <div
      style={{
        backgroundColor: "var(--orange-medium)",
        padding: "8px var(--main-spacing)",
      }}
    >
      <Trans>
        <b>Version de développement de CarbuRe :</b> les manipulations
        effectuées ici n'ont pas de répercussion et les déclarations ne sont pas
        prises en compte.
      </Trans>
    </div>
  )
}

export default Carbure
