import { Column, Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
import { useTranslation } from "react-i18next"
import { Action } from "../types"

export const useQueryScenarioColumns = (): Column<Action>[] => {
  const { t } = useTranslation()

  return [
    { header: t("ID"), key: "id", cell: (row) => row.id },
    { header: t("Type"), key: "type", cell: (row) => row.type },
    {
      header: t("Statut"),
      key: "status",
      cell: (row) => row.status ?? "—",
    },
    { header: t("Quantité"), key: "quantity", cell: (row) => row.quantity },
    {
      header: t("Disponible"),
      key: "available",
      cell: (row) => row.available,
    },
    {
      header: t("Propriétaire"),
      key: "owner_name",
      cell: (row) => row.owner_name,
    },
    {
      header: t("Parent"),
      key: "parent",
      cell: (row) => row.parent ?? "—",
    },
  ]
}

type QueryScenarioTableProps = {
  rows: Action[]
  loading?: boolean
}

export const QueryScenarioTable = ({
  rows,
  loading,
}: QueryScenarioTableProps) => {
  const { t } = useTranslation()
  const columns = useQueryScenarioColumns()

  if (!loading && rows.length === 0) {
    return <NoResult label={t("Aucun résultat")} loading={loading} />
  }

  return <Table rows={rows} columns={columns} loading={loading} />
}
