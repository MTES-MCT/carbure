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
import DoubleCounting from "double-counting"
import Dashboard from "dashboard"
import Controls from "controls"
import Entities from "companies"
import Auth from "auth"
import Saf from "saf/operator"
import SafClient from "saf/airline"
import Stats from "stats"
import Contact from "./components/contact"

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
              <Route path="/contact" element={<Contact />} />
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

  const {
    isAdmin,
    isAuditor,
    isExternal,
    isIndustry,
    isOperator,
    isProducer,
    has_saf,
    isAirline,
  } = entity
  const hasDCA = isExternal && entity.hasAdminRight("DCA")
  const hasAirline = isExternal && entity.hasAdminRight("AIRLINE")

  // prettier-ignore
  return (
    <Routes>
      <Route path="settings" element={<Settings />} />

      {isIndustry &&
        (<>
          <Route path="transactions/:year/*" element={<Transactions />} />
          <Route path="registry" element={<Registry />} />
          <Route path="transactions" element={<Navigate replace to={`${currentYear}`} />} />
          <Route path="*" element={<Navigate replace to="transactions" />} />
        </>
        )}

      {has_saf && isOperator && (<>
        <Route path="saf/:year/*" element={<Saf />} />
        <Route path="saf" element={<Navigate replace to={`${currentYear}/ticket-sources`} />} />
      </>)}

      {isAirline && (<>
        <Route path="saf/:year/*" element={<SafClient />} />
        <Route path="saf" element={<Navigate replace to={`${currentYear}/tickets`} />} />
        <Route path="*" element={<Navigate replace to="saf" />} />
      </>)}

      {isAdmin && (<>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="*" element={<Navigate replace to="dashboard" />} />
      </>)}


      {(isOperator || isProducer) && <Route path="stats" element={<Stats />} />}


      {(isAdmin || isAuditor) && (<>
        <Route path="controls/:year/*" element={<Controls />} />
        <Route path="controls" element={<Navigate replace to={`${currentYear}`} />} />
      </>)}
      {isAuditor && <Route path="*" element={<Navigate replace to="controls" />} />}

      {(isAdmin || hasDCA) && <Route path="double-counting/*" element={<DoubleCounting />} />}
      {hasDCA && <Route path="*" element={<Navigate replace to="double-counting" />} />}

      {(isAdmin || hasAirline) &&
        <Route path="entities/*" element={<Entities />} />
      }
      {hasAirline && <Route path="*" element={<Navigate replace to="entities" />} />}
    </Routes>
  )
}

export default Carbure
