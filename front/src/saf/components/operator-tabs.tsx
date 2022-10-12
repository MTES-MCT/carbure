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
import { SafTicketSourceStatus, SafOperatorSnapshot } from "saf/types"

export interface StatusTabsProps {
  loading: boolean
  count: SafOperatorSnapshot | undefined
}

export const OperatorTabs = ({
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
          key: "ticket-sources",
          path: "ticket-sources",
          label: (
            <StatusRecap
              loading={loading}
              count={count.ticket_sources_volume}
              label={t("Litres à affecter", {
                count: count.ticket_sources_volume,
              })}
            />
          ),
        },
        {
          key: "tickets",
          path: "tickets",
          label: (
            <StatusRecap
              loading={loading}
              count={count.tickets}
              label={t("Tickets envoyés", { count: count.tickets })}
            />
          ),
        },
      ])}
    />
  )
}

const defaultCount: SafOperatorSnapshot = {
  ticket_sources_volume: 0,
  ticket_sources_available: 0,
  ticket_sources_history: 0,
  tickets: 0,
  tickets_pending: 0,
  tickets_rejected: 0,
  tickets_accepted: 0,
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

export function useAutoStatus() {
  const match = useMatch("/org/:entity/saf/:year/ticket-sources/:status") // prettier-ignore
  const status = match?.params.status
  return status ?? SafTicketSourceStatus.Available
}

export default OperatorTabs
