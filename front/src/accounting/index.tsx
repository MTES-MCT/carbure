import { Button } from "common/components/button2"
import {
  ArrowRightLine,
  DraftFill,
  SendPlaneLine,
} from "common/components/icon"
import { Content, Main } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useRoutes } from "common/hooks/routes"
import { Trans, useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import { Operations } from "./pages/operations"
import { Balances } from "./pages/balances"
import { useState } from "react"
import { compact } from "common/utils/collection"
import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"

const MaterialAccounting = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const [operationCount, setOperationCount] = useState(0)
  const entity = useEntity()
  const canTransfer =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)

  return (
    <Main>
      <Button priority="primary" asideX>
        <Trans>Clôturer ma comptabilité mensuelle</Trans>
      </Button>
      <Tabs
        tabs={compact([
          canTransfer && {
            key: "balances",
            label: t("Soldes"),
            path: routes.MATERIAL_ACCOUNTING.BALANCES,
            icon: DraftFill,
          },
          {
            key: "transactions",
            label: `${t("Opérations")} (${operationCount})`,
            path: routes.MATERIAL_ACCOUNTING.OPERATIONS,
            icon: SendPlaneLine,
          },
          {
            key: "teneur",
            label: t("Teneur"),
            path: "##",
            icon: ArrowRightLine,
          },
        ])}
      />
      <Content>
        <Routes>
          <Route
            path="operations"
            element={<Operations setOperationCount={setOperationCount} />}
          />
          {canTransfer && <Route path="balances" element={<Balances />} />}
          <Route path="*" element={<Navigate replace to="operations" />} />
        </Routes>
      </Content>
    </Main>
  )
}

export default MaterialAccounting
