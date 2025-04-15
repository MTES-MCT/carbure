import { DraftFill } from "common/components/icon"
import { Content } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useTranslation } from "react-i18next"
import { Outlet, useParams } from "react-router-dom"
import { compact } from "common/utils/collection"
import { SectorTabs } from "accounting/types"

const OperationsBalancesLayout = () => {
  const { t } = useTranslation()

  // extract current TIRUERT section: "balances" or "operations"
  const params = useParams()
  const [sector] = (params["*"] ?? "").split("/")

  return (
    <>
      <Tabs
        tabs={compact([
          {
            key: SectorTabs.BIOFUELS,
            label: t("Biocarburants"),
            path: `${sector}/${SectorTabs.BIOFUELS}`,
            icon: DraftFill,
          },
          {
            key: SectorTabs.ELEC,
            label: t("Électricité"),
            path: `${sector}/${SectorTabs.ELEC}`,
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
