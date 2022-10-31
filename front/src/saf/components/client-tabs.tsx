import useEntity from "carbure/hooks/entity"
import cl from "clsx"
import { Bell, Loader } from "common/components/icons"
import { Col, Row } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useMatch, useParams } from "react-router-dom"
import css from "./tabs.module.css"

import {
  SafClientSnapshot,
  SafOperatorSnapshot,
  SafTicketSourceStatus,
  SafTicketStatus,
} from "saf/types"

export interface StatusTabsProps {
  loading: boolean
  count?: SafClientSnapshot
}

export const ClientTabs = ({
  loading,
  count = defaultCount,
}: StatusTabsProps) => {
  const entity = useEntity()
  const { t } = useTranslation()

  return (
    <Tabs
      variant="main"
      className={css.safTabs}
      tabs={compact([
        {
          key: "pending",
          path: "tickets/pending",
          label: (
            <Row>
              <Col>
                <p>
                  {loading ? (
                    <Loader size={20} />
                  ) : (
                    formatNumber(count.tickets_pending)
                  )}
                </p>
                <strong>
                  {t("Tickets en attente", {
                    count: count.tickets_pending,
                  })}
                </strong>
              </Col>
            </Row>
          ),
        },
        {
          key: "accepted",
          path: "tickets/accepted",
          label: (
            <Row>
              <Col>
                <p>
                  {loading ? (
                    <Loader size={20} />
                  ) : (
                    formatNumber(count.tickets_accepted)
                  )}
                </p>
                <strong>
                  {t("Tickets acceptés", { count: count.tickets_accepted })}
                </strong>
              </Col>
            </Row>
          ),
        },
      ])}
    />
  )
}

const defaultCount: SafOperatorSnapshot = {
  ticket_sources_available: 0,
  ticket_sources_history: 0,
  tickets: 0,
  tickets_pending: 0,
  tickets_rejected: 0,
  tickets_accepted: 0,
}

interface TicketRecapProps {
  loading: boolean
  count: number
  pending: number
  rejected: number
  label: string
}

export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/saf/tickets/:status/*")
  const status = matchStatus?.params.status as SafTicketStatus
  return status ?? SafTicketStatus.Pending
}

export default ClientTabs
