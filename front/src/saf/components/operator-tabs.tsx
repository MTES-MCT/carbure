import useEntity from "carbure/hooks/entity"
import { Bell, Loader } from "common/components/icons"
import { Col, Row } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useMatch, useParams } from "react-router-dom"
import {
  SafOperatorSnapshot,
  SafTicketSourceStatus,
  SafTicketStatus,
} from "saf/types"

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
  const matchView = useMatch("/org/:entity/saf/:year/:view/*")
  const matchStatus = useMatch("/org/:entity/saf/:year/:view/:status")

  if (matchView?.params.view === "ticket-sources") {
    const status = matchStatus?.params.status as SafTicketSourceStatus
    return status ?? SafTicketSourceStatus.Available
  } else if (matchView?.params.view === "tickets") {
    const status = matchStatus?.params.status as SafTicketStatus
    return status ?? SafTicketStatus.Pending
  } else {
    return SafTicketSourceStatus.Available
  }
}

export default OperatorTabs
