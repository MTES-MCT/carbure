import Account from "account"
import Auth from "auth"
import { PortalProvider } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import Entities from "companies-admin"
import useMissingCompanyInfoModal from "companies/hooks/missing-company-info-modal"
import Controls from "controls"
import DoubleCounting from "double-counting-admin"
import AgreementPublicList from "double-counting/components/agreement-public-list"
import ElecAdmin from "elec-admin"
import ElecAdminAudit from "elec-audit-admin"
import ElecCPO from "elec/cpo"
import ChargePoints from "elec-charge-points/charge-points"
import { ElecOperator } from "elec/operator"
import { Navigate, Route, Routes } from "react-router-dom"
import Registry from "registry"
import SafAirline from "saf/pages/airline"
import SafOperator from "saf/pages/operator"
import Settings from "settings"
import Stats from "stats"
import Transactions from "transactions"
import AccessibilityDeclaration from "./components/accessibility-declaration"
import Home from "./components/home"
import Pending from "./components/pending"
import PublicStats from "./components/public-stats"
import useEntity, { EntityContext, useEntityManager } from "./hooks/entity"
import useUserManager, { UserContext } from "./hooks/user"
import ElecAudit from "elec-auditor"
import { NavigationLayout } from "common/layouts/navigation/navigation-layout"
import { ContactPage } from "contact"
import { YearsProvider } from "common/providers/years-provider"
import { MaterialAccounting } from "accounting"
import { NewNavigationDialog } from "./components/new-navigation-dialog"

const Carbure = () => {
  const user = useUserManager()
  const entity = useEntityManager(user)
  const firstEntity = user.getFirstEntity()
  const isAuth = user.isAuthenticated()

  return (
    <YearsProvider>
      <UserContext.Provider value={user}>
        <EntityContext.Provider value={entity}>
          <PortalProvider>
            <div id="app">
              <NavigationLayout>
                <Routes>
                  {!isAuth && <Route path="*" element={<Home />} />}

                  <Route path="/contact" element={<ContactPage />} />
                  <Route path="/stats" element={<PublicStats />} />
                  <Route
                    path="/double-counting-list"
                    element={<AgreementPublicList />}
                  />
                  <Route
                    path="/accessibilite"
                    element={<AccessibilityDeclaration />}
                  />

                  <Route path="/auth/*" element={<Auth />} />

                  {isAuth && (
                    <>
                      <Route path="/pending" element={<Pending />} />
                      <Route path="/account/*" element={<Account />} />
                      <Route path="/org/:entity/*" element={<Org />} />
                      {entity.isBlank && firstEntity && (
                        <Route
                          path="/"
                          element={
                            <Navigate replace to={`/org/${firstEntity.id}`} />
                          }
                        />
                      )}
                      {entity.isBlank && !firstEntity && (
                        <Route
                          path="/"
                          element={<Navigate replace to={`/pending`} />}
                        />
                      )}
                    </>
                  )}

                  {!user.loading && (
                    <Route path="*" element={<Navigate replace to="/" />} />
                  )}
                </Routes>
                <NewNavigationDialog />
              </NavigationLayout>

              {user.loading && <LoaderOverlay />}
            </div>
          </PortalProvider>
        </EntityContext.Provider>
      </UserContext.Provider>
    </YearsProvider>
  )
}

const currentYear = new Date().getFullYear()

const Org = () => {
  const entity = useEntity()
  useMissingCompanyInfoModal() //TO DELETE WHEN ALL COMPANIES ARE REGISTRED // TO UNCOMMENT TO

  const {
    isAdmin,
    isAuditor,
    isExternal,
    isIndustry,
    isOperator,
    isProducer,
    isAirline,
    isCPO,
    isPowerOrHeatProducer,
    has_saf,
    has_elec,
  } = entity
  const isAdminDC = isExternal && entity.hasAdminRight("DCA")
  const hasAirline = isExternal && entity.hasAdminRight("AIRLINE")
  const isElecAdmin = isExternal && entity.hasAdminRight("ELEC")

  return (
    <Routes>
      <Route path="settings" element={<Settings />} />
      <Route path="registry" element={<Registry />} />
      {(isIndustry || isPowerOrHeatProducer) && (
        <>
          <Route path="accounting/*" element={<MaterialAccounting />} />
          <Route path="transactions/:year/*" element={<Transactions />} />

          <Route
            path="transactions"
            element={<Navigate replace to={`${currentYear}`} />}
          />
          <Route path="*" element={<Navigate replace to="transactions" />} />
        </>
      )}

      {has_saf && isOperator && (
        <>
          <Route path="saf/:year/*" element={<SafOperator />} />
          <Route
            path="saf"
            element={<Navigate replace to={`${currentYear}/ticket-sources`} />}
          />
          <Route
            path="*"
            element={
              <Navigate replace to={`saf/${currentYear}/tickets-sources`} />
            }
          />
        </>
      )}

      {isAirline && (
        <>
          <Route path="saf/:year/*" element={<SafAirline />} />
          <Route
            path="saf"
            element={<Navigate replace to={`${currentYear}/tickets`} />}
          />
          <Route
            path="*"
            element={<Navigate replace to={`saf/${currentYear}/tickets`} />}
          />
        </>
      )}

      {(isOperator || isProducer) && <Route path="stats" element={<Stats />} />}

      {isCPO && (
        <>
          <Route path="elec/:year/*" element={<ElecCPO />} />
          <Route
            path="elec"
            element={<Navigate replace to={`${currentYear}/provisioned`} />}
          />
          <Route
            path="*"
            element={
              <Navigate replace to={`elec/${currentYear}/provisioned`} />
            }
          />
        </>
      )}
      {isOperator && has_elec && (
        <>
          <Route path="elec/:year/*" element={<ElecOperator />} />
          <Route
            path="elec"
            element={<Navigate replace to={`${currentYear}`} />}
          />
          <Route
            path="*"
            element={<Navigate replace to={`elec/${currentYear}/pending`} />}
          />
        </>
      )}
      {((isOperator && has_elec) || isCPO) && (
        <Route path="charge-points/*" element={<ChargePoints />} />
      )}

      {isAuditor && (
        <>
          <Route path="elec-audit/:year/*" element={<ElecAudit />} />
          <Route
            path="elec-audit"
            element={<Navigate replace to={`${currentYear}`} />}
          />
        </>
      )}

      {(isAdmin || isAuditor) && (
        <>
          <Route path="controls/:year/*" element={<Controls />} />
          <Route
            path="controls"
            element={<Navigate replace to={`${currentYear}`} />}
          />
        </>
      )}
      {isAuditor && (
        <Route path="*" element={<Navigate replace to="controls" />} />
      )}

      {(isAdmin || isAdminDC) && (
        <Route path="double-counting/*" element={<DoubleCounting />} />
      )}
      {isAdminDC && (
        <Route path="*" element={<Navigate replace to="double-counting" />} />
      )}

      {(isAdmin || hasAirline || isElecAdmin || isAdminDC) && (
        <>
          <Route path="entities/*" element={<Entities />} />
          <Route path="*" element={<Navigate replace to="entities" />} />
        </>
      )}

      {(isAdmin || isElecAdmin) && (
        <>
          <Route path="elec-admin/:year/*" element={<ElecAdmin />} />
          <Route
            path="elec-admin"
            element={<Navigate replace to={`${currentYear}`} />}
          />
        </>
      )}
      {(isAdmin || isElecAdmin) && (
        <>
          <Route path="elec-admin-audit/:year/*" element={<ElecAdminAudit />} />
          <Route
            path="elec-admin-audit"
            element={<Navigate replace to={`${currentYear}`} />}
          />
        </>
      )}
      {hasAirline && (
        <Route path="*" element={<Navigate replace to="entities" />} />
      )}
    </Routes>
  )
}

export default Carbure
