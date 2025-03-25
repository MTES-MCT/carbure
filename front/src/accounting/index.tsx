import { DraftFill, SendPlaneLine } from "common/components/icon"
import { Content, Main, Row } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes, useLocation } from "react-router-dom"
import { useState } from "react"
import { compact } from "common/utils/collection"
import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"
import { Select } from "common/components/selects2"
import Operations from "./pages/operations"
import Balances from "./pages/balances"
import Teneur from "./pages/teneur"

const MaterialAccounting = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const location = useLocation()
  const [operationCount, setOperationCount] = useState(0)
  const entity = useEntity()
  const canTransfer =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)
  const isTeneurPage = location.pathname.includes(routes.ACCOUNTING.TENEUR)

  return (
    <Main>
      <Row>
        {isTeneurPage && (
          <Select
            options={[{ label: t("Année 2025"), value: 2025 }]}
            value={2025}
            disabled
          />
        )}
      </Row>

      {!isTeneurPage && (
        <Tabs
          tabs={compact([
            canTransfer && {
              key: "balances",
              label: t("Soldes"),
              path: routes.ACCOUNTING.BALANCES,
              icon: DraftFill,
            },
            {
              key: "transactions",
              label: `${t("Opérations")} (${operationCount})`,
              path: routes.ACCOUNTING.OPERATIONS,
              icon: SendPlaneLine,
            },
          ])}
        />
      )}

      <Content style={isTeneurPage ? { marginTop: 0 } : {}}>
        <Routes>
          <Route
            path="operations"
            element={<Operations setOperationCount={setOperationCount} />}
          />
          {canTransfer && (
            <>
              <Route path="balances" element={<Balances />} />
              <Route path="teneur" element={<Teneur />} />
            </>
          )}
          <Route path="*" element={<Navigate replace to="operations" />} />
        </Routes>
      </Content>
    </Main>
  )
}

export default MaterialAccounting
