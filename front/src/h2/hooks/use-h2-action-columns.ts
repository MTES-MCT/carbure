import { useTranslation } from "react-i18next"
import { useActionColumns } from "traceability/hooks/action-columns"

export const useH2ActionColumns = () => {
  const columns = useActionColumns()
  const { t } = useTranslation()

  return {
    ...columns,
    previous_material: {
      ...columns.previous_material,
      header: t("Nature d'H2"),
    },
    site: {
      ...columns.site,
      header: t("Station"),
    },
  }
}
