import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import {
  createSearchParams,
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
import { Container, Content, FooterAuth, Section } from "auth/layouts/container"
import Alert from "@codegouvfr/react-dsfr/Alert"
import { Text } from "common/components/text"

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

  const userInvitedSearchParams = createSearchParams({
    uidb64: uidb64 || "",
    token: activate.result?.data?.token || "",
  })

  return (
    <Container>
      <Content>
        <Section>
          {activate.loading && <LoaderLine style={{ fontSize: "48px" }} />}
          {isSuccess && (
            <Section>
              <Alert
                severity="success"
                description={t("Votre compte a bien été activé !")}
                small
                closable
              />
              <Text>{activatedMessage}</Text>
            </Section>
          )}
          {isError && (
            <Section>
              <Alert
                severity="error"
                description={t(
                  "Une erreur s'est produite lors de l'activation de votre compte."
                )}
                small
                closable
              />
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
                to: "../reset-password",
                state: { search: userInvitedSearchParams.toString() },
              }}
            >
              {t("Définir mon mot de passe")}
            </Button>
          )}
          {isSuccess && !isUserInvited && (
            <Button onClick={() => navigate("../login")}>
              {t("Se connecter")}
            </Button>
          )}
          {isError && !isUserInvited && (
            <Button onClick={() => navigate("../register")}>
              {t("Réessayer de s'inscrire")}
            </Button>
          )}
        </FooterAuth>
      </Content>
    </Container>
  )
}

export const ActivateRequest = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({ email: "" as string | undefined })

  const requestActivationLink = useMutation(api.requestActivateAccount, {
    onSuccess: () => {
      notify(
        t(
          "Si ce compte existe, un nouveau lien d'activation vous a été envoyé"
        ),
        { variant: "success" }
      )
      navigate("../register-pending")
    },

    onError: () => {
      notify(t("Le lien n'a pas pu être envoyé !"), { variant: "danger" })
    },
  })

  return (
    <Container>
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
        <FooterAuth asideX>
          <Button onClick={() => navigate("../register")} priority="secondary">
            {t("Annuler")}
          </Button>
          <Button
            loading={requestActivationLink.loading}
            type="submit"
            nativeButtonProps={{ form: "activate-request" }}
          >
            {t("Renvoyer le lien d'activation")}
          </Button>
        </FooterAuth>
      </Content>
    </Container>
  )
}

export function useToken() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const uidb64 = searchParams.get("uidb64") ?? undefined
  const token = searchParams.get("token") ?? undefined

  useEffect(() => {
    if (uidb64 === undefined || token === undefined) {
      navigate("/")
    }
  }, [uidb64, token, navigate])

  return { uidb64, token }
}
