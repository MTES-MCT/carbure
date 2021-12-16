import { Navigate, Route, Routes } from "react-router-dom"
import { LoaderOverlay } from "common-v2/components/scaffold"
import useUser, { UserContext } from "./hooks/user"
import useEntity from "./hooks/entity"
import DevBanner from "./components/dev-banner"
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
  const user = useUser()

  if (!user.isAuthenticated()) {
    return <Exit to="/accounts/login" />
  }

  return (
    <UserContext.Provider value={user}>
      <div id="app">
        <DevBanner />

        <Topbar />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pending" element={<Pending />} />
          <Route path="/account" element={<Account />} />
          <Route path="/org/:entity/*" element={<Org />} />
          <Route path="/public_stats" element={<PublicStats />} />
          <Route path="/logout" element={<Exit to="/accounts/logout" />} />
        </Routes>

        <Footer />

        {user.loading && <LoaderOverlay />}
      </div>
    </UserContext.Provider>
  )
}

const Org = () => {
  const entity = useEntity()

  const { isAdmin, isAuditor, isExternal, isIndustry } = entity
  const hasDCA = isExternal && entity.hasPage("DCA")

  // prettier-ignore
  return (
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

  )
}

export default Carbure
