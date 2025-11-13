import { Content } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useTranslation } from "react-i18next"
import { Outlet, useParams } from "react-router-dom"
import { compact } from "common/utils/collection"
import { SectorTabs } from "accounting/types"
import useEntity from "common/hooks/entity"

const OperationsBalancesLayout = () => {
  const { t } = useTranslation()
  const { has_elec, isOperator } = useEntity()

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
            icon: "fr-icon-gas-station-fill",
          },
          isOperator &&
            has_elec && {
              key: SectorTabs.ELEC,
              label: t("Électricité"),
              path: `${sector}/${SectorTabs.ELEC}`,
              icon: "fr-icon-charging-pile-2-fill",
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
