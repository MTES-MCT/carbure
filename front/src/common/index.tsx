import { PortalProvider } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import useMissingCompanyInfoModal from "companies/hooks/missing-company-info-modal"
import { Navigate, Route, Routes } from "react-router-dom"
import useEntity, { EntityContext, useEntityManager } from "common/hooks/entity"
import useUserManager, { UserContext, useUser } from "common/hooks/user"
import { NavigationLayout } from "common/layouts/navigation/navigation-layout"
import { YearsProvider } from "common/providers/years-provider"
import { NewNavigationDialog } from "carbure/components/new-navigation-dialog"
import { lazy, Suspense } from "react"
import { BiomethaneRoutes } from "biomethane/routes"

const Account = lazy(() => import("account"))
const Auth = lazy(() => import("auth"))
const Entities = lazy(() => import("companies-admin"))
const Controls = lazy(() => import("controls"))
const DoubleCounting = lazy(() => import("double-counting"))
const DoubleCountingAdmin = lazy(() => import("double-counting-admin"))
const AgreementPublicList = lazy(
  () => import("double-counting/components/agreement-public-list")
)
const ElecAdminAudit = lazy(() => import("elec-audit-admin"))
const ChargePoints = lazy(() => import("elec-charge-points/charge-points"))
const Registry = lazy(() => import("registry"))
const Saf = lazy(() => import("saf"))
const Settings = lazy(() => import("settings"))
const Stats = lazy(() => import("stats"))
const Transactions = lazy(() => import("transactions"))
const Dashboard = lazy(() => import("dashboard"))
const MaterialAccounting = lazy(() => import("accounting"))
const AccessibilityDeclaration = lazy(
  () => import("carbure/components/accessibility-declaration")
)
const Home = lazy(() => import("carbure/components/home"))
const Pending = lazy(() => import("carbure/components/pending"))
const PublicStats = lazy(() => import("carbure/components/public-stats"))
const ElecAudit = lazy(() => import("elec-auditor"))
const ContactPage = lazy(() => import("contact"))
const ElecCertificates = lazy(() => import("elec/pages/certificates"))

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
                <Suspense fallback={<LoaderOverlay />}>
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
                </Suspense>
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
  const user = useUser()
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
    isSafTrader,
    isBiomethaneProducer,
    has_saf,
    accise_number,
  } = entity
  const isAdminDC = isExternal && entity.hasAdminRight("DCA")
  const isSafAdmin = isExternal && entity.hasAdminRight("AIRLINE")
  const isElecAdmin = isExternal && entity.hasAdminRight("ELEC")
  const isElecOperator = isOperator && entity.has_elec
  const isTiruertAdmin = isExternal && entity.hasAdminRight("TIRIB")
  const isTransferElecAdmin =
    isExternal && entity.hasAdminRight("TRANSFERRED_ELEC")
  const userIsMTEDGEC = user?.rights.find(
    (right) => right.entity.name === "MTE - DGEC"
  )
  const isSafOperator = isOperator && has_saf

  return (
    <Routes>
      <Route path="settings/*" element={<Settings />} />
      <Route path="registry" element={<Registry />} />

      {(isIndustry || isPowerOrHeatProducer) && (
        <>
          <Route path="transactions/:year/*" element={<Transactions />} />
          <Route
            path="transactions"
            element={<Navigate replace to={`${currentYear}`} />}
          />
          <Route path="*" element={<Navigate replace to="transactions" />} />
        </>
      )}

      {(userIsMTEDGEC ||
        isAdmin ||
        isTiruertAdmin ||
        isOperator ||
        accise_number !== "") && (
        <Route path="accounting/*" element={<MaterialAccounting />} />
      )}

      {(isAirline || isSafOperator || isSafTrader || isAdmin || isSafAdmin) && (
        <Route path="saf/:year/*" element={<Saf />} />
      )}
      {isProducer && (
        <>
          <Route
            path="double-counting/agreements/*"
            element={<DoubleCounting />}
          />
          <Route
            path="double-counting/*"
            element={<Navigate replace to="agreements" />}
          />
        </>
      )}
      {(isAdmin || isAdminDC) && (
        <Route path="double-counting/*" element={<DoubleCountingAdmin />} />
      )}

      {(isOperator || isProducer) && <Route path="stats" element={<Stats />} />}

      {(isCPO ||
        isElecOperator ||
        isAdmin ||
        isElecAdmin ||
        isTransferElecAdmin) && (
        <Route
          path="elec-v2/certificates/:year/*"
          element={<ElecCertificates />}
        />
      )}

      {(isCPO || isElecAdmin || isAdmin) && (
        <Route path="charge-points/*" element={<ChargePoints />} />
      )}

      {isCPO && (
        <Route
          path=""
          element={
            <Navigate to={`elec-v2/certificates/${currentYear}/provision`} />
          }
        />
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
      {isAdmin && <Route path="dashboard" element={<Dashboard />} />}
      {isAuditor && (
        <Route path="*" element={<Navigate replace to="controls" />} />
      )}

      {isAdminDC && (
        <Route path="*" element={<Navigate replace to="double-counting" />} />
      )}

      {(isAdmin || isExternal) && (
        <>
          <Route path="entities/*" element={<Entities />} />
          <Route path="*" element={<Navigate replace to="entities" />} />
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
      {isSafAdmin && (
        <Route path="*" element={<Navigate replace to="entities" />} />
      )}

      {isBiomethaneProducer && (
        <>
          <Route path="biomethane/*" element={<BiomethaneRoutes />} />
          <Route path="*" element={<Navigate replace to="biomethane" />} />
        </>
      )}
    </Routes>
  )
}

export default Carbure
