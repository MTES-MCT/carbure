import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import {
  createSearchParams,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom"
import { useMutation, useQuery } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { TextInput } from "common/components/inputs2"

import { Button } from "common/components/button2"

import * as api from "../api"
import { LoaderLine } from "common/components/icon"
import { Form, useForm } from "common/components/form2"
import {
  Container,
  Content,
  DialogContainer,
  FooterAuth,
  Section,
} from "auth/layouts/container"
import { Text } from "common/components/text"
import { addQueryParams, ROUTE_URLS } from "common/utils/routes"

export const Activate = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { uidb64, token } = useToken()

  const [searchParams] = useSearchParams()
  const isUserInvited = Boolean(searchParams.get("invite")) || false

  const activate = useQuery(api.activateAccount, {
    key: "activate-account",
    params: [uidb64, token, isUserInvited],
  })

  const isSuccess = activate.status === "success"
  const isError = activate.status === "error"

  const activatedMessage = isUserInvited
    ? t("Vous pouvez maintenant définir votre mot de passe.")
    : t("Vous pouvez maintenant vous connecter sur CarbuRe.")

  const title = isSuccess
    ? t("Votre compte a bien été activé")
    : t("Une erreur s'est produite lors de l'activation de votre compte")

  const userInvitedSearchParams = createSearchParams({
    uidb64: uidb64 || "",
    token: activate.result?.data?.token || "",
  })

  return (
    <Container success={isSuccess} title={title}>
      <Content>
        <Section>
          {activate.loading && <LoaderLine style={{ fontSize: "48px" }} />}
          {isSuccess && (
            <Section>
              <Text>{activatedMessage}</Text>
            </Section>
          )}
          {isError && (
            <Section>
              <Text>
                {t("Merci de recommencer le processus d'inscription.")}
              </Text>
            </Section>
          )}
        </Section>
        <FooterAuth asideX>
          {isUserInvited && (
            <Button
              linkProps={{
                to: addQueryParams(
                  ROUTE_URLS.AUTH.RESET_PASSWORD,
                  Object.fromEntries(userInvitedSearchParams.entries())
                ),
              }}
            >
              {t("Définir mon mot de passe")}
            </Button>
          )}
          {isSuccess && !isUserInvited && (
            <Button onClick={() => navigate(ROUTE_URLS.AUTH.LOGIN)}>
              {t("Se connecter")}
            </Button>
          )}
          {isError && !isUserInvited && (
            <Button onClick={() => navigate(ROUTE_URLS.AUTH.REGISTER)}>
              {t("Réessayer de s'inscrire")}
            </Button>
          )}
        </FooterAuth>
      </Content>
    </Container>
  )
}

type ActivateRequestForm = {
  email?: string
}

export const ActivateRequest = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const location = useLocation()
  const email = (location.state as ActivateRequestForm | null)?.email

  const { value, bind } = useForm<ActivateRequestForm>({
    email: email ?? "",
  })

  const requestActivationLink = useMutation(api.requestActivateAccount, {
    onSuccess: () => {
      notify(
        t(
          "Si ce compte existe, un nouveau lien d'activation vous a été envoyé"
        ),
        { variant: "success" }
      )
      navigate(ROUTE_URLS.AUTH.REGISTER_PENDING)
    },

    onError: () => {
      notify(t("Le lien n'a pas pu être envoyé !"), { variant: "danger" })
    },
  })

  return (
    <DialogContainer
      onClose={() => navigate(ROUTE_URLS.AUTH.REGISTER)}
      title={t("Renvoyer le lien d’activation")}
    >
      <Content>
        <Section>
          {t(
            "Veuillez renseigner votre adresse email afin que nous vous envoyions le lien qui vous permettra d'activer votre compte."
          )}

          <Form
            id="activate-request"
            onSubmit={() => requestActivationLink.execute(value.email!)}
          >
            <TextInput
              autoFocus
              type="email"
              label={t("Adresse email du compte")}
              {...bind("email")}
              required
            />
          </Form>
        </Section>
        <Button
          loading={requestActivationLink.loading}
          type="submit"
          nativeButtonProps={{ form: "activate-request" }}
          asideX
        >
          {t("Renvoyer le lien d'activation")}
        </Button>
      </Content>
    </DialogContainer>
  )
}

export function useToken() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const uidb64 = searchParams.get("uidb64") ?? undefined
  const token = searchParams.get("token") ?? undefined

  useEffect(() => {
    if (uidb64 === undefined || token === undefined) {
      navigate(ROUTE_URLS.HOME)
    }
  }, [uidb64, token, navigate])

  return { uidb64, token }
}
