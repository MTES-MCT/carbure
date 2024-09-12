import Tabs, { TabItem } from "common/components/tabs"
import { useTranslation } from "react-i18next"
import { ChargePointsSnapshot } from "./types"

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
              title={t("Inscriptions")}
              subtitle={snapshot.charge_point_applications}
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
              subtitle={snapshot.meter_reading_applications}
              loading={loading}
            />
          ),
        },
        // {
        //   key: "list",
        //   path: "list",
        //   label: (
        //     <TabItem
        //       title={t("Points de recharge")}
        //       subtitle={snapshot.charge_points}
        //       loading={loading}
        //     />
        //   ),
        // },
      ]}
    />
  )
}
