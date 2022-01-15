import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import { Snapshot, AdminStatus } from "../types"
import Tabs from "common-v2/components/tabs"
import { Loader } from "common-v2/components/icons"
import { formatNumber } from "common-v2/utils/formatters"

export interface StatusTabsProps {
  loading: boolean
  count: Snapshot["lots"] | undefined
}

export const StatusTabs = ({
  loading,
  count = defaultCount,
}: StatusTabsProps) => {
  const { t } = useTranslation()

  return (
    <Tabs
      variant="main"
      tabs={[
        {
          key: "alerts",
          path: "alerts",
          label: (
            <StatusRecap
              loading={loading}
              count={count.alerts}
              label={t("Alertes", { count: count.alerts })}
            />
          ),
        },
        {
          key: "corrections",
          path: "corrections",
          label: (
            <StatusRecap
              loading={loading}
              count={count.corrections}
              label={t("Corrections", { count: count.corrections })}
            />
          ),
        },
        {
          key: "declarations",
          path: "declarations",
          label: (
            <StatusRecap
              loading={loading}
              count={count.declarations}
              label={t("Déclarations", { count: count.declarations })}
            />
          ),
        },
        {
          key: "pinned",
          path: "pinned",
          label: (
            <StatusRecap
              loading={loading}
              count={count.pinned}
              label={t("Lots épinglés", { count: count.pinned })}
            />
          ),
        },
      ]}
    />
  )
}

const defaultCount: Snapshot["lots"] = {
  alerts: 0,
  corrections: 0,
  declarations: 0,
  pinned: 0,
}

interface StatusRecapProps {
  loading: boolean
  count: number
  label: string
  tofix?: number
}

const StatusRecap = ({ loading, count = 0, label }: StatusRecapProps) => {
  const { t } = useTranslation()

  return (
    <>
      <p>{loading ? <Loader size={20} /> : formatNumber(count)} </p>
      <strong>{label}</strong>
    </>
  )
}

export function useStatus() {
  const match = useMatch<"status", string>("/org/:entity/controls/:year/:status/*") // prettier-ignore
  return (match?.params.status ?? "unknown") as AdminStatus
}

export default StatusTabs
