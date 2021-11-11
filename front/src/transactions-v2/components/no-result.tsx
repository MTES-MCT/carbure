import Alert from "common-v2/components/alert"
import Button from "common-v2/components/button"
import { AlertCircle } from "common-v2/components/icons"
import { useTranslation } from "react-i18next"

interface NoResultProps extends ResetButtonProps {
  loading: boolean
}

export const NoResult = ({ loading, count, onReset }: NoResultProps) => {
  const { t } = useTranslation()

  return (
    <Alert loading={loading} variant="warning" icon={AlertCircle}>
      <p>{t("Aucune transaction trouvée pour cette recherche")}</p>
      <ResetButton count={count} onReset={onReset} />
    </Alert>
  )
}

interface ResetButtonProps {
  count: number
  onReset: () => void
}

export const ResetButton = ({ count, onReset }: ResetButtonProps) => {
  const { t } = useTranslation()
  return (
    <Button asideX variant="link" action={onReset}>
      {t("Réinitialiser les filtres")}
      <span>({count})</span>
    </Button>
  )
}

export default NoResult
