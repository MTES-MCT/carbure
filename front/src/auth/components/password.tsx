import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { useNavigate } from "react-router-dom"

import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"
import { useToken } from "./activate"
import { Form, useForm } from "common/components/form2"
import { Container, Content, FooterAuth, Section } from "auth/layouts/container"
import { TextInput } from "common/components/inputs2"
import { PasswordInput, usePasswordValidation } from "./password-input"
import { Text } from "common/components/text"
import Alert from "@codegouvfr/react-dsfr/Alert"

export const ResetPasswordRequest = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({ email: "" as string | undefined })

  const requestPasswordReset = useMutation(api.requestResetPassword, {
    onSuccess: () => {
      notify(t("La demande de changement de mot de passe a été envoyée !"), {
        variant: "success",
      })
      navigate("../reset-password-pending")
    },

    onError: () => {
      notify(t("La demande n'a pas pu être envoyée !"), { variant: "danger" })
    },
  })

  return (
    <Container>
      <Content>
        <Section>
          <p>
            {t(
              "Veuillez renseigner votre adresse email afin que nous vous envoyions les instructions pour réinitialiser votre mot de passe."
            )}
          </p>
          <Form
            id="reset-password-request"
            onSubmit={() => requestPasswordReset.execute(value.email!)}
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
          <Button onClick={() => navigate("../login")} priority="secondary">
            {t("Annuler")}
          </Button>
          <Button
            loading={requestPasswordReset.loading}
            disabled={!value.email}
            type="submit"
            nativeButtonProps={{ form: "reset-password-request" }}
          >
            {t("Demander une réinitialisation")}
          </Button>
        </FooterAuth>
      </Content>
    </Container>
  )
}

export const ResetPasswordPending = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <Container>
      <Content>
        <Section>
          <Alert
            severity="success"
            description={t(
              "Votre demande de réinitialisation de mot de passe a bien été envoyée !"
            )}
            small
            closable
          />
          <Text>
            {t(
              "Si un compte existe avec cet email, vous recevrez un email sous peu contenant un lien qui vous permettra de modifier votre mot de passe."
            )}
          </Text>
        </Section>

        <FooterAuth asideX>
          <Button priority="secondary" onClick={() => navigate("/")}>
            {t("Retour")}
          </Button>
        </FooterAuth>
      </Content>
    </Container>
  )
}

export const ResetPassword = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const navigate = useNavigate()

  const { value, bind } = useForm({
    newPassword: "" as string | undefined,
    repeatNewPassword: "" as string | undefined,
  })

  const { uidb64, token } = useToken()

  const resetPassword = useMutation(api.resetPassword, {
    onSuccess: () => {
      notify(t("Le mot de passe a bien été changé !"), { variant: "success" })
      navigate("../login")
    },

    onError: (error) => {
      notifyError(error)
    },
  })

  const { isValid } = usePasswordValidation(
    value.newPassword,
    value.repeatNewPassword
  )

  const onSubmit = () => {
    if (!isValid) return
    resetPassword.execute(
      uidb64,
      token,
      value.newPassword!,
      value.repeatNewPassword!
    )
  }

  return (
    <Container>
      <Content>
        <Section>
          <Text>
            {t(
              "Vous pouvez maintenant modifier votre mot de passe en renseignant les champs ci-dessous"
            )}
          </Text>

          <Form id="reset-password" onSubmit={onSubmit}>
            <PasswordInput
              label={t("Mot de passe")}
              {...bind("newPassword")}
              autoComplete="new-password"
              required
            />
            <PasswordInput
              label={t("Répéter le mot de passe")}
              {...bind("repeatNewPassword")}
              confirm={value.newPassword}
              autoComplete="new-password"
              required
            />
          </Form>
        </Section>
        <FooterAuth>
          <Button onClick={() => navigate("/")} priority="secondary">
            {t("Annuler")}
          </Button>
          <Button
            loading={resetPassword.loading}
            type="submit"
            nativeButtonProps={{ form: "reset-password" }}
          >
            {t("Enregistrer le mot de passe")}
          </Button>
        </FooterAuth>
      </Content>
    </Container>
  )
}
