import Alert from "common-v2/components/alert"
import Button from "common-v2/components/button"
import { AlertCircle } from "common-v2/components/icons"
import { useTranslation } from "react-i18next"

interface NoResultProps {
  loading: boolean
  filterCount: number
  onReset: () => void
}

export const NoResult = ({ loading, filterCount, onReset }: NoResultProps) => {
  const { t } = useTranslation()

  return (
    <Alert loading={loading} variant="warning" icon={AlertCircle}>
      <p>{t("Aucun résultat trouvé pour cette recherche")}</p>

      <Button
        aside
        variant="link"
        label={t("Réinitialiser les filtres ({{amount}})", {
          amount: filterCount,
        })}
        action={onReset}
      />
    </Alert>
  )
}

export default NoResult
