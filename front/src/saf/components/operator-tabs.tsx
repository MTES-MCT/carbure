import cl from "clsx"
import { Bell, Loader } from "common/components/icons"
import { Col, Row } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import css from "./tabs.module.css"

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
  const { t } = useTranslation()

  return (
    <Tabs
      variant="main"
      className={css.safTabs}
      tabs={compact([
        {
          key: "ticket-sources",
          path: "ticket-sources",
          label: (
            <Row>
              <Col>
                <p>
                  {loading ? (
                    <Loader size={20} />
                  ) : (
                    formatNumber(count.ticket_sources_available)
                  )}
                </p>
                <strong>
                  {t("Volumes disponibles", {
                    count: count.ticket_sources_available,
                  })}
                </strong>
              </Col>
            </Row>
          ),
        },
        {
          key: "tickets-received",
          path: "tickets-received",
          label: (
            <TicketReceived
              loading={loading}
              count={count.tickets_received}
              pending={count.tickets_received_pending}
              label={t("Tickets reçus", { count: count.tickets_received })}
            />
          ),
        },
        {
          key: "tickets-assigned",
          path:
            count.tickets_assigned_rejected > 0
              ? "tickets-assigned/rejected"
              : "tickets-assigned",
          label: (
            <TicketAssigned
              loading={loading}
              count={count.tickets_assigned}
              rejected={count.tickets_assigned_rejected}
              label={t("Tickets affectés", { count: count.tickets_assigned })}
            />
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
  tickets_assigned: 0,
  tickets_assigned_accepted: 0,
  tickets_assigned_pending: 0,
  tickets_assigned_rejected: 0,
  tickets_received: 0,
  tickets_received_accepted: 0,
  tickets_received_pending: 0,
}

interface TicketReceivedProps {
  loading: boolean
  count: number
  pending: number
  label: string
}

const TicketReceived = ({
  loading,
  count = 0,
  pending = 0,
  label,
}: TicketReceivedProps) => {
  const { t } = useTranslation()
  const hasAlert = pending > 0

  return (
    <>
      <Row className={cl(hasAlert && css.recto)}>
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
        <Col className={css.verso}>
          {pending > 0 && (
            <p>
              <strong>{formatNumber(pending)}</strong>{" "}
              {t("tickets en attente", { count: pending })}
            </p>
          )}
        </Col>
      )}
    </>
  )
}

interface TicketAssignedProps {
  loading: boolean
  count: number
  rejected: number
  label: string
}

const TicketAssigned = ({
  loading,
  count = 0,
  rejected = 0,
  label,
}: TicketAssignedProps) => {
  const { t } = useTranslation()
  const hasAlert = rejected > 0

  return (
    <>
      <Row className={cl(hasAlert && css.recto)}>
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
        <Col className={css.verso}>
          {rejected > 0 && (
            <p>
              <strong>{formatNumber(rejected)}</strong>{" "}
              {t("tickets refusés", { count: rejected })}
            </p>
          )}
        </Col>
      )}
    </>
  )
}

export function useAutoStatus() {
  const matchView = useMatch("/org/:entity/saf/:year/:view/*")
  const matchStatus = useMatch("/org/:entity/saf/:year/:view/:status")

  if (!matchView) {
    return SafTicketSourceStatus.Available
  }

  if (matchView.params.view === "ticket-sources") {
    //TODO afficher la categorie non vide en premier au chargement
    // cf transactions/components/category.tsx -> useAutoCategory
    // if (snapshot.ticket_sources_available > 0)
    //   return SafTicketSourceStatus.Available
    // else if (snapshot.ticket_sources_history > 0)
    //   return SafTicketSourceStatus.History

    const status =
      matchStatus?.params?.status?.toUpperCase() as SafTicketSourceStatus
    return status ?? SafTicketSourceStatus.Available
  }

  if (
    matchView.params.view === "tickets-assigned" ||
    matchView.params.view === "tickets-received"
  ) {
    const status = matchStatus?.params?.status?.toUpperCase() as SafTicketStatus
    return status ?? SafTicketStatus.Pending
  }

  return SafTicketSourceStatus.Available
}

export default OperatorTabs
