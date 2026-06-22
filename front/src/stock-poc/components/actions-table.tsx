import { Button } from "common/components/button2"
import { Column, Table } from "common/components/table2"
import { Row } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { Action } from "../types"

export const ActionsTable = ({
  actions,
  loading,
  showOwner = true,
  onEdit,
  onDelete,
}: {
  actions: Action[]
  loading?: boolean
  showOwner?: boolean
  onEdit?: (action: Action) => void
  onDelete?: (action: Action) => void
}) => {
  const { t } = useTranslation()

  const columns: Column<Action>[] = [
    { header: t("ID"), cell: (a) => `#${a.id}`, small: true },
    { header: t("Type"), cell: (a) => a.type },
    { header: t("Statut"), cell: (a) => a.status ?? "—" },
    { header: t("Quantité"), cell: (a) => a.quantity },
    { header: t("Disponible"), cell: (a) => a.available },
    { header: t("Parent"), cell: (a) => (a.parent ? `#${a.parent}` : "—") },
  ]

  if (showOwner) {
    columns.push({ header: t("Propriétaire"), cell: (a) => a.owner_name })
  }

  if (onEdit || onDelete) {
    columns.push({
      header: t("Actions"),
      small: true,
      cell: (a) => (
        <Row gap="sm">
          {onEdit && (
            <Button
              priority="tertiary no outline"
              iconId="ri-pencil-line"
              title={t("Modifier")}
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                onEdit(a)
              }}
            />
          )}
          {onDelete && (
            <Button
              priority="tertiary no outline"
              iconId="ri-delete-bin-line"
              title={t("Supprimer")}
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(a)
              }}
            />
          )}
        </Row>
      ),
    })
  }

  return <Table columns={columns} rows={actions} loading={loading} />
}
