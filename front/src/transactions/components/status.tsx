import cl from "clsx"
import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import { Snapshot, Status } from "../types"
import Tabs from "common-v2/components/tabs"
import { AlertCircle, Loader } from "common-v2/components/icons"
import { Col, Row } from "common-v2/components/scaffold"
import css from "./status.module.css"
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
      className={css.statusTabs}
      tabs={[
        {
          key: "draft",
          path: "drafts",
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
              count={count.in_total}
              pending={count.in_pending}
              tofix={count.in_tofix}
              label={t("Lots reçus", { count: count.in_pending })}
            />
          ),
        },
        {
          key: "stock",
          path: "stocks",
          label: (
            <StatusRecap
              loading={loading}
              count={count.stock}
              label={t("Lots en stock", { count: count.stock })}
            />
          ),
        },
        {
          key: "out",
          path: "out",
          label: (
            <StatusRecap
              loading={loading}
              count={count.out_total}
              pending={count.out_pending}
              tofix={count.out_tofix}
              label={t("Lots envoyés", { count: count.out_pending })}
            />
          ),
        },
      ]}
    />
  )
}

const defaultCount: Snapshot["lots"] = {
  draft: 0,
  in_pending: 0,
  in_tofix: 0,
  in_total: 0,
  stock: 0,
  stock_total: 0,
  out_pending: 0,
  out_tofix: 0,
  out_total: 0,
}

interface StatusRecapProps {
  loading: boolean
  count: number
  label: string
  pending?: number
  tofix?: number
}

const StatusRecap = ({
  loading,
  count = 0,
  pending = 0,
  tofix = 0,
  label,
}: StatusRecapProps) => {
  const { t } = useTranslation()
  const hasAlert = pending > 0 || tofix > 0

  return (
    <>
      <Row className={cl(hasAlert && css.recto)}>
        <Col>
          <p>{loading ? <Loader size={20} /> : count}</p>
          <strong>{label}</strong>
        </Col>

        {hasAlert && (
          <Col
            style={{
              marginLeft: "auto",
              alignItems: "flex-end",
              justifyContent: "center",
            }}
          >
            <AlertCircle size={32} color="var(--orange-dark)" />
          </Col>
        )}
      </Row>

      {hasAlert && (
        <Col className={css.verso}>
          {pending > 0 && (
            <p>
              <strong>{pending}</strong> {t("lots en attente")}
            </p>
          )}
          {tofix > 0 && (
            <p>
              <strong>{tofix}</strong> {t("lots à corriger")}
            </p>
          )}
        </Col>
      )}
    </>
  )
}

export function useStatus() {
  const match = useMatch<"status", string>("/org/:entity/transactions/:status/*") // prettier-ignore
  return (match?.params.status ?? "unknown") as Status
}

export default StatusTabs
