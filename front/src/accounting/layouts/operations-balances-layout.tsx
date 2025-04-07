import { DraftFill, SendPlaneLine } from "common/components/icon"
import { Content } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { Outlet } from "react-router-dom"
import { compact } from "common/utils/collection"
import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"

const OperationsBalancesLayout = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const entity = useEntity()
  const canTransfer =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)
  return (
    <>
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
            label: `${t("Opérations")}`,
            path: routes.ACCOUNTING.OPERATIONS,
            icon: SendPlaneLine,
          },
        ])}
      />

      <Content>
        <Outlet />
      </Content>
    </>
  )
}

export default OperationsBalancesLayout
