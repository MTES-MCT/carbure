import Alert from "common-v2/components/alert"
import Button from "common-v2/components/button"
import { AlertCircle } from "common-v2/components/icons"
import { useTranslation } from "react-i18next"
import { FilterManager } from "./filters"

interface NoResultProps {
  loading: boolean
  filters: FilterManager
}

export const NoResult = ({ loading, filters }: NoResultProps) => {
  const { t } = useTranslation()

  return (
    <Alert loading={loading} variant="warning" icon={AlertCircle}>
      <p>{t("Aucune transaction trouvée pour cette recherche")}</p>
      <ResetButton filters={filters} />
    </Alert>
  )
}

interface ResetButtonProps {
  filters: FilterManager
}

export const ResetButton = ({ filters }: ResetButtonProps) => {
  const { t } = useTranslation()
  return (
    <>
      <Button asideX variant="link" action={filters.resetFilters}>
        {t("Réinitialiser les filtres")}
      </Button>
      <span>({filters.count})</span>
    </>
  )
}

export default NoResult
