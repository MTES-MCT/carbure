import { useTranslation } from "react-i18next"
import Tabs from "common-v2/components/tabs"
import { Column } from "common-v2/components/scaffold"
import { Snapshot } from "transactions-v2/types"
import { Loader } from "common-v2/components/icons"

const defaultCount: Snapshot["lots"] = {
  draft: 0,
  in_accepted: 0,
  in_pending: 0,
  in_tofix: 0,
  in_total: 0,
  stock: 0,
  out_accepted: 0,
  out_pending: 0,
  out_tofix: 0,
  out_total: 0,
}

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
          key: "draft",
          path: "draft",
          label: (
            <StatusRecap
              loading={loading}
              count={count.draft}
              label={t("Brouillon", { count: count.draft })}
            />
          ),
        },
        {
          key: "in",
          path: "in",
          label: (
            <StatusRecap
              loading={loading}
              count={count.in_pending}
              tofix={count.in_tofix}
              label={t("Entrées", { count: count.in_pending })}
            />
          ),
        },
        {
          key: "stock",
          path: "stock",
          label: (
            <StatusRecap
              loading={loading}
              count={count.stock}
              label={t("Stock", { count: count.stock })}
            />
          ),
        },
        {
          key: "out",
          path: "out",
          label: (
            <StatusRecap
              loading={loading}
              count={count.out_pending}
              tofix={count.out_tofix}
              label={t("Sorties", { count: count.out_pending })}
            />
          ),
        },
      ]}
    />
  )
}

interface StatusRecapProps {
  loading: boolean
  count: number
  label: string
  tofix?: number
}

const StatusRecap = ({
  loading,
  count = 0,
  tofix = 0,
  label,
}: StatusRecapProps) => {
  const { t } = useTranslation()

  return (
    <>
      <p>
        {loading ? <Loader size={16} /> : count}{" "}
        {tofix > 0 && (
          <small>
            ({tofix} {t("à corriger")})
          </small>
        )}
      </p>
      <strong>{label}</strong>
    </>
  )
}

export default StatusTabs
