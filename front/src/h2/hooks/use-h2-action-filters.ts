import { useTranslation } from "react-i18next"
import { useActionFilters } from "traceability/hooks/use-action-filters"

export const useH2ActionFilters = () => {
  const filters = useActionFilters()
  const { t } = useTranslation()

  return {
    ...filters,
    previous_material: {
      ...filters.previous_material,
      label: t("Nature d'H2"),
    },
    site: {
      ...filters.site,
      label: t("Station"),
    },
  }
}
