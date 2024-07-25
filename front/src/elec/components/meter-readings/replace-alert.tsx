import Alert from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { Trans } from "react-i18next"

export const ReplaceAlert = () => {
  return (
    <Alert icon={AlertCircle} variant="warning">
      <Trans>
        Des relevés pour la même période sont déjà en attente de validation.
        Cette nouvelle demande viendra écraser la précédente.
      </Trans>
    </Alert>
  )
}
