import { useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import * as api from "../../api"
import { ActivationScreen, useActivationLink } from "./activation-link"

export function useActivate(): ActivationScreen {
  const { t } = useTranslation()
  const { uidb64, token, activated, invalidLink } = useActivationLink()

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

  if (activate.status === "error") {
    return invalidLink
  }

  return { success: false, title: errorTitle }
}
