import Table, { Cell, Order } from "common/components/table"
import { compact } from "common/utils/collection"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"
import { SafTicket, SafTicketStatus } from "saf/types"
import TicketTag from "./tag"

export interface TicketsTableProps {
  loading: boolean
  status: SafTicketStatus
  tickets: SafTicket[]
  order: Order | undefined
  rowLink: (ticketSource: SafTicket) => To
  onOrder: (order: Order | undefined) => void
}

export const TicketsTable = memo(
  ({
    loading,
    tickets,
    order,
    rowLink,
    onOrder,
    status,
  }: TicketsTableProps) => {
    const columns = useColumns(status)
    return (
      <Table
        loading={loading}
        order={order}
        onOrder={onOrder}
        rowLink={rowLink}
        rows={tickets}
        columns={compact([
          columns.status,
          columns.client,
          columns.availableVolume,
          columns.period,
          columns.feedstock,
          columns.ghgReduction,
        ])}
      />
    )
  }
)

export function useColumns(status: SafTicketStatus) {
  const { t } = useTranslation()

  return {
    status: {
      header: t("Statut"),
      cell: (ticket: SafTicket) => (
        <TicketTag ticket={ticket} status={status} />
      ),
    },

    availableVolume: {
      header: t("Volume"),
      cell: (ticket: SafTicket) => (
        <Cell text={`${formatNumber(ticket.volume)} L`} />
      ),
    },

    client: {
      header: t("Client"),
      cell: (ticket: SafTicket) => <Cell text={ticket.client_name} />,
    },

    period: {
      key: "period",
      header: t("Période"),
      cell: (ticket: SafTicket) => (
        <Cell
          text={formatPeriod(ticket.period)}
          sub={formatDate(ticket.date)}
        />
      ),
    },

    feedstock: {
      key: "feedstock",
      header: t("Matière première"),
      cell: (ticket: SafTicket) => (
        <Cell
          text={t(ticket.feedstock?.code ?? "", { ns: "feedstocks" })}
          sub={t(ticket.country_of_origin?.code_pays ?? "", {
            ns: "countries",
          })}
        />
      ),
    },

    ghgReduction: {
      small: true,
      key: "ghg_reduction",
      header: t("Réd. GES"),
      cell: (ticket: SafTicket) => (
        <Cell text={`${ticket.ghg_reduction.toFixed(2)}%`} />
      ),
    },
  }
}

export default TicketsTable
