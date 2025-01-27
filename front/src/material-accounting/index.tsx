import { Button } from "common/components/button2"
import {
  ArrowRightLine,
  DraftFill,
  SendPlaneLine,
} from "common/components/icon"
import { Content, Main } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { Route, Routes } from "react-router-dom"
import { Operations } from "./operations"
import { Balance } from "./balance"
export const MaterialAccounting = () => {
  const { t } = useTranslation()
  const routes = useRoutes()

  return (
    <Main>
      <Button priority="primary" asideX>
        Clôturer ma comptabilité mensuelle
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
            label: t("Opérations"),
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
          <Route path="operations" element={<Operations />} />
          <Route path="balance" element={<Balance />} />
        </Routes>
      </Content>
    </Main>
  )
}
