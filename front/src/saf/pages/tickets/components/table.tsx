import { compact } from "common/utils/collection"
import { formatNumber, formatPeriod } from "common/utils/formatters"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"
import {
  SafStates,
  SafTicketPreview,
  SafTicketsResponse,
  SafTicketStatus,
} from "saf/types"
import TicketTag from "saf/components/ticket-tag"
import { Order, Table, Cell, Column } from "common/components/table2"
import { Pagination } from "common/components/pagination2/pagination"
import { NoResult } from "common/components/no-result2"
import { formatConsumptionType } from "saf/utils/formatters"
import useEntity from "common/hooks/entity"

export interface TicketsTableProps {
  loading: boolean
  state: SafStates
  actions: any
  status: SafTicketStatus
  ticketsData?: SafTicketsResponse
  order: Order | undefined
  client?: boolean
  rowLink: (ticket: SafTicketPreview) => To
}

export const TicketsTable = memo(
  ({
    loading,
    state,
    actions,
    ticketsData,
    order,
    client,
    rowLink,
  }: TicketsTableProps) => {
    const entity = useEntity()
    const columns = useColumns()

    const isAdmin = entity.isAdmin || entity.isExternal

    const total = ticketsData?.count ?? 0
    const count = ticketsData?.results.length ?? 0
    const tickets = ticketsData?.results

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
                !isAdmin && (client ? columns.supplier : columns.client),
                isAdmin && columns.supplier,
                isAdmin && columns.client,
                columns.availableVolume,
                columns.period,
                columns.feedstock,
                columns.consumption,
                columns.ghgReduction,
              ])}
            />

            <Pagination
              defaultPage={state.page}
              limit={state.limit}
              total={total}
              onLimit={actions.setLimit}
            />
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
      cell: (ticket) => (
        <TicketTag
          status={ticket.status}
          ets={"ets_status" in ticket ? ticket.ets_status : undefined}
        />
      ),
    },

    availableVolume: {
      key: "volume",
      header: t("Volume"),
      cell: (ticket) => <Cell text={`${formatNumber(ticket.volume)} L`} />,
    },

    client: {
      key: "client",
      header: t("Client"),
      cell: (ticket) => <Cell text={ticket.client} />,
    },

    supplier: {
      key: "supplier",
      header: t("Fournisseur"),
      cell: (ticket) => <Cell text={ticket.supplier} />,
    },

    period: {
      key: "period",
      header: t("Période"),
      cell: (ticket) => (
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
      cell: (ticket) => (
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
      cell: (ticket) => <Cell text={`${ticket.ghg_reduction?.toFixed(0)}%`} />,
    },

    consumption: {
      key: "consumption_type",
      header: t("Type de consommation"),
      cell: (ticket) => (
        <Cell
          text={
            ticket.consumption_type
              ? formatConsumptionType(ticket.consumption_type)
              : "-"
          }
        />
      ),
    },
  } satisfies Record<string, Column<SafTicketPreview>>
}

export default TicketsTable
