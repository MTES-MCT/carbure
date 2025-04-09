import { DraftFill } from "common/components/icon"
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
            key: SectorTabs.BIOFUELS,
            label: t("Biocarburants"),
            path: `operations/${SectorTabs.BIOFUELS}`,
            icon: DraftFill,
          },
          {
            key: SectorTabs.ELEC,
            label: t("Électricité"),
            path: `operations/${SectorTabs.ELEC}`,
            icon: DraftFill,
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
