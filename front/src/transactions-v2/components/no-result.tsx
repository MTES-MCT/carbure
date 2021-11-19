import { useTranslation } from "react-i18next"
import Alert from "common-v2/components/alert"
import { AlertCircle } from "common-v2/components/icons"
import { FilterManager, ResetButton } from "./filters"

interface NoResultProps {
  loading?: boolean
  filters?: FilterManager
}

export const NoResult = ({ loading, filters }: NoResultProps) => {
  const { t } = useTranslation()

  return (
    <Alert loading={loading} variant="warning" icon={AlertCircle}>
      <p>{t("Aucun résultat trouvé pour cette recherche")}</p>
      {filters && <ResetButton filters={filters} />}
    </Alert>
  )
}

export default NoResult
