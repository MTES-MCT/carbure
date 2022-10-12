import Table, { Order } from "common/components/table"
import { compact } from "common/utils/collection"
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
        columns={compact([columns.status])}
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
  }
}

export default TicketSourcesTable
