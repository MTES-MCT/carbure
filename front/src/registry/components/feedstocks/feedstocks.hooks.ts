import { useMemo } from "react"
import { Column } from "common/components/table2"
import { FeedStockClassification } from "common/types"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"

export const useFeedstocksColumns = () => {
  const entity = useEntity()
  const { t } = useTranslation()

  // For now, the new classification system is set for admin and biomethane entities
  // Display the legacy classification system for other entities
  const displayNewClassification =
    entity.isAdmin || entity.isRelatedToBiomethane()

  const columns = useMemo<Column<FeedStockClassification>[]>(() => {
    if (displayNewClassification) {
      return [
        {
          key: "name",
          header: t("Matière première"),
          cell: (e) => e.name,
          orderBy: (e) => e.name,
        },
        {
          key: "group",
          header: t("Type"),
          cell: (e) => e.classification?.group,
          orderBy: (e) => e.name,
        },
        {
          key: "category",
          header: t("Catégorie"),
          cell: (e) => e.classification?.category,
          orderBy: (e) => e.classification?.category ?? "",
        },
        {
          key: "subcategory",
          header: t("Sous-catégorie"),
          cell: (e) => e.classification?.subcategory,
          orderBy: (e) => e.classification?.subcategory ?? "",
        },
      ]
    }
    return [
      {
        key: "name",
        header: t("Matière première"),
        cell: (e) => e.name,
        orderBy: (e) => e.name,
      },
      {
        key: "category",
        header: t("Catégorie"),
        cell: (e) => e.category,
        orderBy: (e) => e.category ?? "",
      },
    ]
  }, [displayNewClassification, t])

  return columns
}
