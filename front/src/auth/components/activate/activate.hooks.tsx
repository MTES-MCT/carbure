import { useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import * as api from "../../api"
import { ActivationScreen, useActivationResend } from "./activation-link"

export function useActivate(): ActivationScreen {
  const { t } = useTranslation()
  const { uidb64, token, activated, resendResult, resendButton } =
    useActivationResend()

  const activate = useQuery(api.activateAccount, {
    key: "activate-account",
    params: [uidb64, token],
  })

  const errorTitle = t(
    "Une erreur s'est produite lors de l'activation de votre compte"
  )

  if (activate.loading) {
    return { success: false, loading: true, title: errorTitle }
  }

  if (activate.status === "success") {
    return activated
  }

  if (resendResult) {
    return resendResult
  }

  if (activate.status === "error") {
    return {
      success: false,
      title: errorTitle,
      message: t(
        "Ce lien n'est plus valable : il a expiré ou a déjà été utilisé. Demandez un nouveau lien pour activer votre compte."
      ),
      action: resendButton,
    }
  }

  return { success: false, title: errorTitle }
}
