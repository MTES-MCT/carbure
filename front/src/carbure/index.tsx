import { Navigate, Route, Routes } from "react-router-dom"
import { LoaderOverlay } from "common/components/scaffold"
import useUserManager, { UserContext } from "./hooks/user"
import useEntity, { EntityContext, useEntityManager } from "./hooks/entity"
import { PortalProvider } from "common/components/portal"
import Topbar from "./components/top-bar"
import Footer from "./components/footer"
import Pending from "./components/pending"
import Registry from "registry"
import PublicStats from "./components/public-stats"
import Home from "./components/home"
import Transactions from "transactions"
import Settings from "settings"
import Account from "account"
import DoubleCounting from "doublecount"
import Dashboard from "dashboard"
import Controls from "controls"
import Entities from "companies"
import Auth from "auth"

const Carbure = () => {
  const user = useUserManager()
  const entity = useEntityManager(user)

  const isAuth = user.isAuthenticated()

  return (
    <UserContext.Provider value={user}>
      <EntityContext.Provider value={entity}>
        <PortalProvider>
          <div id="app">
            <Topbar />

            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/stats" element={<PublicStats />} />

              <Route path="/auth/*" element={<Auth />} />

              {isAuth && <Route path="/pending" element={<Pending />} />}
              {isAuth && <Route path="/account" element={<Account />} />}
              {isAuth && <Route path="/org/:entity/*" element={<Org />} />}

              {!user.loading && (
                <Route path="*" element={<Navigate replace to="/" />} />
              )}
            </Routes>

            <Footer />

            {user.loading && <LoaderOverlay />}
          </div>
        </PortalProvider>
      </EntityContext.Provider>
    </UserContext.Provider>
  )
}

const currentYear = new Date().getFullYear()

const Org = () => {
  const entity = useEntity()

  const { isAdmin, isAuditor, isExternal, isIndustry } = entity
  const hasDCA = isExternal && entity.hasPage("DCA")

  // prettier-ignore
  return (
      <Routes>
        <Route path="settings" element={<Settings />} />

        {isIndustry && <Route path="transactions/:year/*" element={<Transactions />} />}
        {isIndustry && <Route path="registry" element={<Registry />} />}

        {isAdmin && <Route path="dashboard" element={<Dashboard />} />}
        {isAdmin && <Route path="entities/*" element={<Entities />} />}

        {(isAdmin || isAuditor) && <Route path="controls/:year/*" element={<Controls />} />}
        {(isAdmin || hasDCA) && <Route path="double-counting/*" element={<DoubleCounting />} />}

        {isIndustry && <Route path="transactions" element={<Navigate replace to={`${currentYear}`} />} />}
        {(isAdmin || isAuditor) && <Route path="controls" element={<Navigate replace to={`${currentYear}`} />} />}

        {isIndustry && <Route path="*" element={<Navigate replace to="transactions" />} />}
        {isAuditor && <Route path="*" element={<Navigate replace to="controls" />} />}
        {isAdmin && <Route path="*" element={<Navigate replace to="dashboard" />} />}
        {hasDCA && <Route path="*" element={<Navigate replace to="double-counting" />} />}
      </Routes>
  )
}

export default Carbure
