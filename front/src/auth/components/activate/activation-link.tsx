import { ReactNode, useState } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { Button } from "common/components/button2"
import { LoaderLine } from "common/components/icon"
import { useNotify } from "common/components/notifications"
import { Text } from "common/components/text"
import { useMutation } from "common/hooks/async"
import { ROUTE_URLS } from "common/utils/routes"
import { Container, Content, FooterAuth, Section } from "auth/layouts/container"
import * as api from "../../api"
import { useToken } from "./use-token"

export const ACCOUNT_ALREADY_ACTIVE = "ACCOUNT_ALREADY_ACTIVE"
export const ACTIVATION_LINK_ERROR = "Could not send activation link"
export const ACTIVATION_FAILED = "Could not activate user account"

export type ActivationScreen = {
  success: boolean
  title: string
  message?: string
  action?: ReactNode
  form?: ReactNode
  loading?: boolean
}

export function ActivationLayout({
  success,
  title,
  loading,
  message,
  form,
  action,
}: ActivationScreen) {
  return (
    <Container success={success} title={title}>
      <Content>
        <Section>
          {loading && <LoaderLine style={{ fontSize: "48px" }} />}
          {message && <Text>{message}</Text>}
          {form}
        </Section>
        {action && <FooterAuth asideX>{action}</FooterAuth>}
      </Content>
    </Container>
  )
}

export function apiMessage(error: unknown): string | undefined {
  if (typeof error !== "object" || error === null || !("data" in error)) {
    return undefined
  }
  const data = (error as { data?: { message?: string } }).data
  return data?.message
}

// Both links carry the same uid and token. Resending it, and the screens that
// follow, do not depend on which page opened the link.
export function useActivationResend() {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const { uidb64, token } = useToken()
  const [linkResent, setLinkResent] = useState(false)
  const [resendFailure, setResendFailure] = useState<string | null>(null)
  const resendActivationLink = useMutation(api.resendActivationLink, {
    onSuccess: () => setLinkResent(true),
    onError: (error) => {
      const message = apiMessage(error)
      if (
        message === ACCOUNT_ALREADY_ACTIVE ||
        message === ACTIVATION_LINK_ERROR
      ) {
        setResendFailure(message)
        return
      }
      notify(t("Le lien n'a pas pu être envoyé !"), { variant: "danger" })
    },
  })

  const login = (
    <Button onClick={() => navigate(ROUTE_URLS.AUTH.LOGIN)}>
      {t("Se connecter")}
    </Button>
  )

  const activated: ActivationScreen = {
    success: true,
    title: t("Votre compte a bien été activé"),
    message: t("Vous pouvez maintenant vous connecter sur CarbuRe."),
    action: login,
  }

  let resendResult: ActivationScreen | undefined
  if (linkResent) {
    resendResult = {
      success: false,
      title: t("Un nouveau lien d'activation a été envoyé"),
      message: t(
        "Il a été envoyé à l'adresse email de ce compte. Pensez à vérifier vos courriers indésirables."
      ),
    }
  } else if (resendFailure === ACCOUNT_ALREADY_ACTIVE) {
    resendResult = {
      success: false,
      title: t("Votre compte est déjà activé"),
      message: t("Vous pouvez vous connecter sur CarbuRe."),
      action: login,
    }
  } else if (resendFailure === ACTIVATION_LINK_ERROR) {
    resendResult = {
      success: false,
      title: t("Ce lien ne permet pas de renvoyer le mail"),
      message: t(
        "Indiquez l'adresse email du compte pour recevoir un nouveau lien d'activation."
      ),
      action: (
        <Button linkProps={{ to: ROUTE_URLS.AUTH.ACTIVATE_REQUEST }}>
          {t("Indiquer mon adresse email")}
        </Button>
      ),
    }
  }

  const resendButton = (
    <Button
      loading={resendActivationLink.loading}
      disabled={!uidb64 || !token}
      onClick={() => {
        if (uidb64 && token) resendActivationLink.execute(uidb64, token)
      }}
    >
      {t("Renvoyer le lien d'activation")}
    </Button>
  )

  return { uidb64, token, activated, resendResult, resendButton }
}
