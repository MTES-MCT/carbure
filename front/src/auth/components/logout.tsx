import { useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { LoaderOverlay } from "common/components/scaffold"
import { COMMON_QUERY_KEYS, useMutation } from "common/hooks/async-rq"
import * as api from "../api"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"

export const Logout = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const hasTriggeredLogout = useRef(false)

  const logoutMutation = useMutation({
    mutationFn: api.logout,
    invalidates: [COMMON_QUERY_KEYS.userSettings],
    onSuccess: () => {
      notify(t("Vous êtes déconnecté !"), { variant: "success" })
      navigate("/")
    },
    onError: () => {
      notify(t("La déconnexion a échoué !"), { variant: "danger" })
    },
  })

  useEffect(() => {
    // Prevent duplicate mutation calls in React StrictMode.
    if (hasTriggeredLogout.current) return
    hasTriggeredLogout.current = true
    logoutMutation.mutate()
  }, [logoutMutation])

  return <LoaderOverlay />
}
