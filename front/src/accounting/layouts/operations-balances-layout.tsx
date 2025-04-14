import { Content } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useTranslation } from "react-i18next"
import { Outlet } from "react-router-dom"
import { compact } from "common/utils/collection"
import { SectorTabs } from "accounting/types"

const OperationsBalancesLayout = () => {
  const { t } = useTranslation()

  return (
    <>
      <Tabs
        tabs={compact([
          {
            key: "balances",
            label: t("Biocarburants"),
            path: SectorTabs.BIOFUELS,
            icon: "ri-draft-fill",
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
