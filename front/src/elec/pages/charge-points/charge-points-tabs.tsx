import Tabs, { TabItem } from "common/components/tabs"
import { useTranslation } from "react-i18next"
import { ChargePointsSnapshot } from "../../types-charge-points"

type ChargePointsTabsProps = {
  loading: boolean
  snapshot: ChargePointsSnapshot
}

export const ChargePointsTabs = ({
  loading,
  snapshot,
}: ChargePointsTabsProps) => {
  const { t } = useTranslation()

  return (
    <Tabs
      variant="main"
      tabs={[
        {
          key: "pending",
          path: "pending",
          label: (
            <TabItem
              title={t("Inscriptions de points de recharge")}
              subtitle={snapshot.charge_points_pending}
              loading={loading}
            />
          ),
        },
        {
          key: "meter-readings",
          path: "meter-readings",
          label: (
            <TabItem
              title={t("Relevés trimestriels")}
              subtitle={snapshot.meter_reading}
              loading={loading}
            />
          ),
        },
        {
          key: "list",
          path: "list",
          label: (
            <TabItem
              title={t("Points de recharge inscrits")}
              subtitle={snapshot.charge_points_pending}
              loading={loading}
            />
          ),
        },
      ]}
    />
  )
}
