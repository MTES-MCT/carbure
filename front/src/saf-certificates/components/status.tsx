import cl from "clsx"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useMatch, useNavigate } from "react-router-dom"
import { Snapshot, Status } from "../../transactions/types"
import Tabs from "common/components/tabs"
import { Bell, Loader } from "common/components/icons"
import { Col, Row } from "common/components/scaffold"
import { formatNumber } from "common/utils/formatters"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"

export interface StatusTabsProps {
  loading: boolean
  count: Snapshot["lots"] | undefined
}

export const StatusTabs = ({
  loading,
  count = defaultCount,
}: StatusTabsProps) => {
  const entity = useEntity()
  const { t } = useTranslation()

  return (
    <Tabs
      variant="main"
      tabs={compact([
        {
          key: "to-assign",
          path: "to-assign",
          label: (
            <StatusRecap
              loading={loading}
              count={count.draft}
              label={t("Lots SAF", { count: count.draft })}
            />
          ),
        },
        {
          key: "pending",
          path: "pending",
          label: (
            <StatusRecap
              loading={loading}
              count={count.in_total}
              pending={count.in_pending}
              tofix={count.in_tofix}
              label={t("Certificats en attente", { count: count.in_total })}
            />
          ),
        },
        {
          key: "accepted",
          path: "accepted",
          label: (
            <StatusRecap
              loading={loading}
              count={count.in_total}
              pending={count.in_pending}
              tofix={count.in_tofix}
              label={t("Certificats refusés", { count: count.in_total })}
            />
          ),
        },
        {
          key: "rejected",
          path: "rejected",
          label: (
            <StatusRecap
              loading={loading}
              count={count.in_total}
              pending={count.in_pending}
              tofix={count.in_tofix}
              label={t("Certificats acceptés", { count: count.in_total })}
            />
          ),
        },
      ])}
    />
  )
}

const defaultCount: Snapshot["lots"] = {
  draft_imported: 0,
  draft_stocks: 0,
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
      <Row>
        <Col>
          <p>{loading ? <Loader size={20} /> : formatNumber(count)}</p>
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
            <Bell
              size={32}
              color="var(--orange-dark)"
              style={{ transform: "rotate(45deg)" }}
            />
          </Col>
        )}
      </Row>

      {hasAlert && (
        <Col>
          {pending > 0 && (
            <p>
              <strong>{formatNumber(pending)}</strong>{" "}
              {t("lots en attente", { count: pending })}
            </p>
          )}
          {tofix > 0 && (
            <p>
              <strong>{formatNumber(tofix)}</strong>{" "}
              {t("lots à corriger", { count: tofix })}
            </p>
          )}
        </Col>
      )}
    </>
  )
}

export function useStatus() {
  const match = useMatch("/org/:entity/transactions/:year/:status/*") // prettier-ignore
  const status = match?.params.status as Status | undefined
  return status ?? "drafts"
}

export function useAutoStatus() {
  const navigate = useNavigate()
  const match = useMatch("/org/:entity/transactions/:year/:status/*") // prettier-ignore
  const status = match?.params.status as Status | undefined

  useEffect(() => {
    if (status === undefined) {
      navigate("drafts/imported", { replace: true })
    }
  }, [status, navigate])

  return status ?? "drafts"
}

export default StatusTabs
