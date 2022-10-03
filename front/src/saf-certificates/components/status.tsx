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
import { SafCertificateStatus, SafSnapshot } from "saf-certificates/types"

export interface StatusTabsProps {
  loading: boolean
  count: SafSnapshot | undefined
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
              count={count.to_assign}
              label={t("Lots SAF", { count: count.to_assign })}
            />
          ),
        },
        {
          key: "pending",
          path: "pending",
          label: (
            <StatusRecap
              loading={loading}
              count={count.pending}
              label={t("Certificats en attente", { count: count.pending })}
            />
          ),
        },
        {
          key: "accepted",
          path: "accepted",
          label: (
            <StatusRecap
              loading={loading}
              count={count.rejected}
              hasAlert={!!count.rejected}
              label={t("Certificats refusés", { count: count.rejected })}
            />
          ),
        },
        {
          key: "rejected",
          path: "rejected",
          label: (
            <StatusRecap
              loading={loading}
              count={count.accepted}
              label={t("Certificats acceptés", { count: count.accepted })}
            />
          ),
        },
      ])}
    />
  )
}

const defaultCount: SafSnapshot = {
  to_assign: 0,
  to_assign_available: 0,
  to_assign_history: 0,
  pending: 0,
  rejected: 0,
  accepted: 0,
}

interface StatusRecapProps {
  loading: boolean
  count: number
  label: string
  hasAlert?: boolean
}

const StatusRecap = ({
  loading,
  count = 0,
  hasAlert = false,
  label,
}: StatusRecapProps) => {
  const { t } = useTranslation()

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
