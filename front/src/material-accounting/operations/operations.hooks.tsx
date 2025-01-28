import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"

import { apiTypes } from "common/services/api-fetch.types"
import { OperationBadge } from "./components/operation-badge"
import { formatDate, formatNumber } from "common/utils/formatters"
import { Text } from "common/components/text"
import { formatOperationType, formatSector } from "./operations.utils"
import useEntity from "carbure/hooks/entity"

export const useOperationsColumns = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const columns: Column<apiTypes["OperationOutput"]>[] = [
    {
      key: "status",
      header: t("Statut"),
      cell: (item) => <OperationBadge status={item.status} />,
    },
    {
      key: "sector",
      header: t("Filière"),
      cell: (item) => (
        <Text
          size="sm"
          fontWeight="bold"
          style={{ color: "var(--info-425-625)" }}
          is="button"
        >
          {t(formatSector(item.sector))}
        </Text>
      ),
    },
    {
      key: "biofuel",
      header: t("Biocarburant"),
      cell: (item) => item.biofuel,
    },
    {
      key: "category",
      header: t("Catégorie"),
      cell: (item) => item.customs_category,
    },
    {
      key: "created_at",
      header: t("Date"),
      cell: (item) => formatDate(item.created_at),
    },
    {
      key: "depot",
      header: t("Dépot"),
      cell: (item) => <Cell text={item.from_depot?.name ?? "-"} />,
    },
    {
      key: "operation_type",
      header: t("Opération"),
      cell: (item) => <Cell text={t(formatOperationType(item.type))} />,
    },
    // {
    //   key: "from_to",
    //   header: t("De/à"),
    //   // @ts-ignore toto
    //   cell: (item) => "-",
    // },
    {
      key: "volume",
      header: t("Volume"),
      cell: (item) =>
        item.debited_entity?.id === entity.id ? (
          <Text
            size="sm"
            fontWeight="semibold"
            style={{ color: "var(--text-default-error)" }}
          >
            -{formatNumber(Number(item.volume))}
          </Text>
        ) : (
          <Text
            size="sm"
            fontWeight="semibold"
            style={{ color: "var(--text-default-success)" }}
          >
            +{formatNumber(Number(item.volume))}
          </Text>
        ),
    },
  ]

  return columns
}
