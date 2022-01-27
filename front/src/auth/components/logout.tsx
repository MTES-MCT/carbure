import { useNavigate } from "react-router-dom"
import { useQuery } from "common-v2/hooks/async"
import { LoaderOverlay } from "common-v2/components/scaffold"
import { invalidate } from "common-v2/hooks/invalidate"
import * as api from "../api"
import { useNotify } from "common-v2/components/notifications"
import { useTranslation } from "react-i18next"

export const Logout = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  // automatically run logout request when this component is loaded
  useQuery(api.logout, {
    key: "logout",
    params: [],
    onSuccess: () => {
      invalidate("user-settings")
      notify(t("Vous êtes déconnecté !"), { variant: "success" })
      navigate("/")
    },
    onError: () => {
      notify(t("La déconnexion a échoué !"), { variant: "danger" })
    },
  })

  return <LoaderOverlay />
}
