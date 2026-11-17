import { ReactNode, useState } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { Button } from "common/components/button2"
import { LoaderLine } from "common/components/icon"
import { Text } from "common/components/text"
import { ROUTE_URLS } from "common/utils/routes"
import { Container, Content, FooterAuth, Section } from "auth/layouts/container"
import { ActivateRequest } from "./activate-request"
import { useToken } from "./use-token"

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

// The join page and the self-registration activation page share the same link check.
export function useActivationLink() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { uidb64, token } = useToken()
  const [requestOpen, setRequestOpen] = useState(false)

  const activated: ActivationScreen = {
    success: true,
    title: t("Votre compte a bien été activé"),
    message: t("Vous pouvez maintenant vous connecter sur CarbuRe."),
    action: (
      <Button onClick={() => navigate(ROUTE_URLS.AUTH.LOGIN)}>
        {t("Se connecter")}
      </Button>
    ),
  }

  const invalidLink: ActivationScreen = {
    success: false,
    title: t("Ce lien n'est pas valide"),
    message: t(
      "Renseignez l'adresse email du compte pour recevoir un nouveau lien d'activation."
    ),
    action: (
      <>
        <Button onClick={() => setRequestOpen(true)}>
          {t("Renseigner mon email")}
        </Button>
        {requestOpen && (
          <ActivateRequest onClose={() => setRequestOpen(false)} />
        )}
      </>
    ),
  }

  return { uidb64, token, activated, invalidLink }
}
