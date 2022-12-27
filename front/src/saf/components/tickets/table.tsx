import useEntity from "carbure/hooks/entity"
import Pagination from "common/components/pagination"
import Table, { Cell, Order } from "common/components/table"
import { compact } from "common/utils/collection"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"
import {
  SafStates,
  SafTicket,
  SafTicketsResponse,
  SafTicketStatus,
} from "saf/types"
import NoResult from "../no-result"
import TicketTag from "./tag"

export interface TicketsTableProps {
  loading: boolean
  state: SafStates
  actions: any
  status: SafTicketStatus
  ticketsData?: SafTicketsResponse
  order: Order | undefined
  rowLink: (ticketSource: SafTicket) => To
}

export const TicketsTable = memo(
  ({
    loading,
    state,
    actions,
    ticketsData,
    order,
    rowLink,
  }: TicketsTableProps) => {
    const { isAirline } = useEntity()
    const columns = useColumns()

    const total = ticketsData?.total ?? 0
    const count = ticketsData?.returned ?? 0
    const tickets = ticketsData?.saf_tickets

    return (
      <>
        {count > 0 && tickets ? (
          <>
            <Table
              loading={loading}
              order={order}
              onOrder={actions.setOrder}
              rowLink={rowLink}
              rows={tickets}
              columns={compact([
                columns.status,
                isAirline ? columns.supplier : columns.client,
                columns.availableVolume,
                columns.period,
                columns.feedstock,
                columns.ghgReduction,
              ])}
            />
            {/* <TicketsTable
            loading={false}
            order={state.order}
            status={status as SafTicketStatus}
            tickets={tickets}
            rowLink={showTicketDetail}
            onOrder={actions.setOrder}
          /> */}

            {(state.limit || 0) < total && (
              <Pagination
                page={state.page}
                limit={state.limit}
                total={total}
                onPage={actions.setPage}
                onLimit={actions.setLimit}
              />
            )}
          </>
        ) : (
          <NoResult
            loading={!ticketsData}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}
      </>
    )
  }
)

export function useColumns() {
  const { t } = useTranslation()

  return {
    status: {
      header: t("Statut"),
      cell: (ticket: SafTicket) => <TicketTag status={ticket.status} />,
    },

    availableVolume: {
      key: "volume",
      header: t("Volume"),
      cell: (ticket: SafTicket) => (
        <Cell text={`${formatNumber(ticket.volume)} L`} />
      ),
    },

    client: {
      key: "client",
      header: t("Client"),
      cell: (ticket: SafTicket) => <Cell text={ticket.client} />,
    },

    supplier: {
      key: "supplier",
      header: t("Fournisseur"),
      cell: (ticket: SafTicket) => <Cell text={ticket.supplier} />,
    },

    period: {
      key: "period",
      header: t("Période"),
      cell: (ticket: SafTicket) => (
        <Cell
          text={
            ticket.assignment_period
              ? formatPeriod(ticket.assignment_period)
              : t("N/A")
          }
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
        <Cell text={`${ticket.ghg_reduction.toFixed(0)}%`} />
      ),
    },
  }
}

export default TicketsTable
