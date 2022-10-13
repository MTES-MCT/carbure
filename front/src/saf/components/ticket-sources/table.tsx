import Table, { Cell, Order } from "common/components/table"
import { compact } from "common/utils/collection"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { isRedII } from "lot-add/components/ghg-fields"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"
import { SafTicketSource } from "saf/types"
import { TicketSourceTag } from "./tag"

export interface TicketSourcesTableProps {
  loading: boolean
  ticketSources: SafTicketSource[]
  order: Order | undefined
  rowLink: (ticketSource: SafTicketSource) => To
  onOrder: (order: Order | undefined) => void
}

export const TicketSourcesTable = memo(
  ({
    loading,
    ticketSources,
    order,
    rowLink,
    onOrder,
  }: TicketSourcesTableProps) => {
    const columns = useColumns()
    return (
      <Table
        loading={loading}
        order={order}
        onOrder={onOrder}
        rowLink={rowLink}
        rows={ticketSources}
        columns={compact([
          columns.status,
          columns.availableVolume,
          columns.period,
          columns.feedstock,
          columns.ghgReduction,
        ])}
      />
    )
  }
)

export function useColumns() {
  const { t } = useTranslation()

  return {
    status: {
      header: t("Statut"),
      cell: (ticketSource: SafTicketSource) => (
        <TicketSourceTag ticketSource={ticketSource} />
      ),
    },

    availableVolume: {
      header: t("Volume disponible"),
      cell: (ticketSource: SafTicketSource) => (
        <Cell
          text={`${formatNumber(
            ticketSource.total_volume - ticketSource.assigned_volume
          )} L`}
          sub={`/${formatNumber(ticketSource.total_volume)} L`}
        />
      ),
    },

    period: {
      key: "period",
      header: t("Période"),
      cell: (ticketSource: SafTicketSource) => (
        <Cell
          text={formatPeriod(ticketSource.period)}
          sub={formatDate(ticketSource.date)}
        />
      ),
    },

    feedstock: {
      key: "feedstock",
      header: t("Matière première"),
      cell: (ticketSource: SafTicketSource) => (
        <Cell
          text={t(ticketSource.feedstock?.code ?? "", { ns: "feedstocks" })}
          sub={t(ticketSource.country_of_origin?.code_pays ?? "", {
            ns: "countries",
          })}
        />
      ),
    },

    ghgReduction: {
      small: true,
      key: "ghg_reduction",
      header: t("Réd. GES"),
      cell: (ticketSource: SafTicketSource) => {
        return <Cell text={`${ticketSource.ghg_reduction.toFixed(2)}%`} />
      },
    },
  }
}

export default TicketSourcesTable
