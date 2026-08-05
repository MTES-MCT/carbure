import { Cell, Column, Order, Table } from "common/components/table2"
import { Action } from "h2/types"
import { useTranslation } from "react-i18next"

type ActionTableProps = {
  actions: Action[]
  loading: boolean
  order?: Order
  onOrder: (order: Order | undefined) => void
}
export const ActionTable = ({
  actions,
  loading,
  order,
  onOrder,
}: ActionTableProps) => {
  const { t } = useTranslation()
  const columns: Column<Action>[] = [
    {
      key: "id",
      header: "Id",
      cell: (action) => <Cell text={action.id} />,
    },
    {
      key: "holder",
      header: t("Holder"),
      cell: (action) => <Cell text={action.holder} />,
    },
    {
      key: "industry",
      header: t("Raffinerie"),
      cell: (action) => <Cell text={action.industry} />,
    },
    {
      key: "material",
      header: t("Nature d'H2"),
      cell: (action) => <Cell text={action.material} />,
    },
    {
      key: "quantity",
      header: t("Quantité"),
      cell: (action) => <Cell text={action.quantity} />,
    },
  ]

  const showAction = () => {}

  return (
    <Table
      loading={loading}
      columns={columns}
      rows={actions}
      order={order}
      onOrder={onOrder}
      onAction={showAction}
    />
  )
}
