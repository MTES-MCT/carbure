import { useTranslation } from "react-i18next"
import Alert from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { FilterManager, ResetButton } from "../../transactions/components/filters"

interface NoResultProps extends Partial<FilterManager> {
  loading?: boolean
  label?: string
}

export const NoResult = ({ loading, filters, onFilter, label }: NoResultProps) => {
  const { t } = useTranslation()

  return (
    <Alert loading={loading} variant="warning" icon={AlertCircle}>
      <p>
        {loading
          ? t("Chargement en cours...")
          : label || t("Aucun résultat trouvé pour cette recherche")}
      </p>
      {filters && onFilter && (
        <ResetButton filters={filters} onFilter={onFilter} />
      )}
    </Alert>
  )
}

export default NoResult
