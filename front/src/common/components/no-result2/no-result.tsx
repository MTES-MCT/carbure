import { CBQueryFilterManager } from "common/hooks/query-builder-2"
import { Notice } from "../notice"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"

interface NoResultProps extends Partial<CBQueryFilterManager> {
  loading?: boolean
  label?: string
}

function countFilters(filters: CBQueryFilterManager["filters"]) {
  if (filters === undefined) return 0
  return Object.values(filters).reduce((total, list) => total + list.length, 0)
}

export const NoResult = ({
  loading,
  filters,
  onFilter,
  label,
}: NoResultProps) => {
  const { t } = useTranslation()

  const hasFilters = useMemo(() => {
    return Object.values(filters ?? {}).some((filter) => filter.length > 0)
  }, [filters])

  return (
    <Notice
      variant="warning"
      title={
        loading
          ? t("Chargement en cours...")
          : (label ?? t("Aucun résultat trouvé pour cette recherche"))
      }
      linkText={
        hasFilters && filters
          ? `${t("Réinitialiser les filtres")} (${countFilters(filters)})`
          : undefined
      }
      onAction={() => {
        if (hasFilters && filters && onFilter) {
          onFilter({})
        }
      }}
    />
  )
}
