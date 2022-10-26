import Alert from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { useTranslation } from "react-i18next"
import { SafFilterSelection } from "saf/types"
import { ResetButton } from "transactions/components/filters"

export interface FilterManager {
  filters: SafFilterSelection
  onFilter: (filters: SafFilterSelection) => void
}

interface NoResultProps extends Partial<FilterManager> {
  loading?: boolean
}

export const NoResult = ({ loading, filters, onFilter }: NoResultProps) => {
  const { t } = useTranslation()

  return (
    <Alert loading={loading} variant="warning" icon={AlertCircle}>
      <p>{t("Aucun résultat trouvé pour cette recherche")}</p>
      {filters && onFilter && Object.keys(filters).length && (
        <ResetButton filters={filters} onFilter={onFilter} />
      )}
    </Alert>
  )
}

export default NoResult
