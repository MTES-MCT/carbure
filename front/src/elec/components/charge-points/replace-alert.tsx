import Alert from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { Trans } from "react-i18next"

export const ReplaceAlert = () => {
  return (
    <Alert icon={AlertCircle} variant="warning">
      <Trans>
        Vous avez déjà une demande d'inscription en attente. Cette nouvelle
        demande viendra écraser la précédente.
      </Trans>
    </Alert>
  )
}
