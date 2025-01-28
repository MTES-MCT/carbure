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
import { Route, Routes } from "react-router-dom"
import { Operations } from "./operations"
import { Balance } from "./balance"
import { useState } from "react"
export const MaterialAccounting = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const [operationCount, setOperationCount] = useState(0)

  return (
    <Main>
      <Button priority="primary" asideX>
        <Trans>Clôturer ma comptabilité mensuelle</Trans>
      </Button>
      <Tabs
        tabs={[
          {
            key: "balance",
            label: t("Soldes"),
            path: routes.MATERIAL_ACCOUNTING.BALANCE,
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
        ]}
      />
      <Content>
        <Routes>
          <Route
            path="operations"
            element={<Operations setOperationCount={setOperationCount} />}
          />
          <Route path="balance" element={<Balance />} />
        </Routes>
      </Content>
    </Main>
  )
}
