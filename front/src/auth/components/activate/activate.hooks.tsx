import { ReactNode, useState } from "react"
import { useTranslation } from "react-i18next"
import {
  createSearchParams,
  useNavigate,
  useSearchParams,
} from "react-router-dom"
import { useMutation, useQuery } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { Button } from "common/components/button2"
import { addQueryParams, ROUTE_URLS } from "common/utils/routes"
import * as api from "../../api"
import { useToken } from "./use-token"

type ActivationContent = {
  success: boolean
  loading: boolean
  title: string
  message?: string
  action?: ReactNode
}

export function useActivate(): ActivationContent {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const { uidb64, token } = useToken()
  const [searchParams] = useSearchParams()
  const isUserInvited = Boolean(searchParams.get("invite"))

  const activate = useQuery(api.activateAccount, {
    key: "activate-account",
    params: [uidb64, token],
  })
  const [linkResent, setLinkResent] = useState(false)
  const resendActivationLink = useMutation(api.resendActivationLink, {
    onSuccess: () => setLinkResent(true),
    onError: () => {
      notify(t("Le lien n'a pas pu être envoyé !"), { variant: "danger" })
    },
  })

  const errorTitle = t(
    "Une erreur s'est produite lors de l'activation de votre compte"
  )

  if (activate.loading) {
    return { success: false, loading: true, title: errorTitle }
  }

  if (activate.status === "success") {
    const passwordParams = createSearchParams({
      uidb64: uidb64 || "",
      token: activate.result?.data?.token || "",
    })

    return {
      success: true,
      loading: false,
      title: t("Votre compte a bien été activé"),
      message: isUserInvited
        ? t("Vous pouvez maintenant définir votre mot de passe.")
        : t("Vous pouvez maintenant vous connecter sur CarbuRe."),
      action: isUserInvited ? (
        <Button
          linkProps={{
            to: addQueryParams(
              ROUTE_URLS.AUTH.RESET_PASSWORD,
              Object.fromEntries(passwordParams.entries())
            ),
          }}
        >
          {t("Définir mon mot de passe")}
        </Button>
      ) : (
        <Button onClick={() => navigate(ROUTE_URLS.AUTH.LOGIN)}>
          {t("Se connecter")}
        </Button>
      ),
    }
  }

  if (linkResent) {
    return {
      success: false,
      loading: false,
      title: t("Un nouveau lien d'activation a été envoyé"),
      message: t(
        "Il a été envoyé à l'adresse email de ce compte. Pensez à vérifier vos courriers indésirables."
      ),
    }
  }

  if (activate.status === "error") {
    return {
      success: false,
      loading: false,
      title: errorTitle,
      message: t(
        "Ce lien n'est plus valable : il a expiré ou a déjà été utilisé. Demandez un nouveau lien pour activer votre compte."
      ),
      action: (
        <Button
          loading={resendActivationLink.loading}
          disabled={!uidb64 || !token}
          onClick={() => {
            if (uidb64 && token) resendActivationLink.execute(uidb64, token)
          }}
        >
          {t("Renvoyer le lien d'activation")}
        </Button>
      ),
    }
  }

  return { success: false, loading: false, title: errorTitle }
}
