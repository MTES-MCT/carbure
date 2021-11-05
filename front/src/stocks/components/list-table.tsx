import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

import { Lots, LotStatus, Transaction, UserRole } from "common/types"
import { SortingSelection } from "transactions/hooks/query/use-sort-by" // prettier-ignore
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { StatusSelection } from "transactions/hooks/query/use-status"


import Table, { Actions, arrow, Row } from "common/components/table"
import * as C from "transactions/components/list-columns"
import { Edit } from "common/components/icons"
import { LotSender } from "stocks/hooks/use-send-lots"
import { useRights } from "carbure/hooks/use-rights"

type StockTableProps = {
  stock: Lots | null
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  sender: LotSender
}

export const StockTable = ({
  stock,
  status,
  sorting,
  selection,
  sender,
}: StockTableProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const rights = useRights()
  const createDrafts = sender.createDrafts

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  const columns = []

  if (status.is(LotStatus.Inbox)) {
    columns.push(
      C.selector(selection),
      C.periodSimple(t),
      C.dae(t),
      C.biocarburant(t),
      C.matierePremiere(t),
      C.vendor(t),
      C.origine(t),
      C.depot(t),
      C.ghgReduction(t),
      arrow
    )
  }

  if (status.is(LotStatus.Stock)) {
    const actions = Actions([
      {
        icon: Edit,
        title: t("Préparer l'envoi"),
        action: createDrafts,
      },
    ])

    columns.push(
      C.selector(selection),
      C.periodSimple(t),
      C.carbureID(t),
      C.biocarburantInStock(t),
      C.matierePremiere(t),
      C.vendor(t),
      C.origine(t),
      C.depot(t),
      C.ghgReduction(t),
      canModify ? actions : arrow
    )
  }

  if (status.is(LotStatus.ToSend)) {
    columns.push(
      C.selector(selection),
      C.periodSimple(t),
      C.dae(t),
      C.biocarburant(t),
      C.matierePremiere(t),
      C.client(t),
      C.origine(t),
      C.destination(t),
      C.ghgReduction(t),
      arrow
    )
  }

  if (stock === null) {
    return null
  }

  const rows: Row<Transaction>[] = stock.lots.map((tx) => ({
    value: tx,
    onClick: () => navigate(`${tx.id}`),
  }))

  return (
    <Table
      columns={columns}
      rows={rows}
      sortBy={sorting.column}
      order={sorting.order}
      onSort={sorting.sortBy}
    />
  )
}
