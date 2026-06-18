import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { Form, useForm } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"
import { Container, Content, FooterAuth } from "auth/layouts/container"
import { Title } from "common/components/title"
import {
  PasswordInput,
  usePasswordValidation,
} from "auth/components/password-input"

export const Register = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const navigate = useNavigate()

  const { value, bind, setField } = useForm({
    email: "" as string | undefined,
    name: "" as string | undefined,
    password: "" as string | undefined,
    repeatPassword: "" as string | undefined,
  })

  const register = useMutation(api.register, {
    onSuccess: () => {
      notify(t("Le compte a bien été créé !"), { variant: "success" })
      navigate("../register-pending")
    },

    onError: (error) => {
      notifyError(error)
    },
  })

  const { messages, confirmationMessages, isValid } = usePasswordValidation(
    value.password,
    value.repeatPassword
  )

  return (
    <Container>
      <Title is="h1" as="h3" style={{ textAlign: "center" }}>
        {t("Inscription")}
      </Title>

      <Content>
        <Form
          id="register"
          gap="sm"
          onSubmit={() =>
            register.execute(
              value.email!,
              value.name!,
              value.password!,
              value.repeatPassword!
            )
          }
        >
          <TextInput
            autoFocus
            type="email"
            label={t("Adresse email")}
            {...bind("email")}
            required
          />
          <TextInput
            placeholder="Jean-François CHAMPOLLION"
            label={t("Nom")}
            {...bind("name")}
            required
          />
          <PasswordInput
            label={t("Mot de passe")}
            value={value.password}
            onChange={(v) => setField("password", v)}
            messages={messages}
            autoComplete="new-password"
            required
          />
          <PasswordInput
            label={t("Répéter le mot de passe")}
            value={value.repeatPassword}
            onChange={(v) => setField("repeatPassword", v)}
            messages={confirmationMessages}
            messagesHint=""
            autoComplete="new-password"
            required
          />
        </Form>

        <Button
          customPriority="link"
          linkProps={{ to: "../activate-request" }}
          center
        >
          {t("Je n'ai pas reçu le lien d'activation")}
        </Button>
        <FooterAuth>
          <Button priority="secondary" linkProps={{ to: "/" }}>
            {t("Annuler")}
          </Button>
          <Button
            loading={register.loading}
            disabled={!isValid || !value.email || !value.name}
            type="submit"
            nativeButtonProps={{ form: "register" }}
          >
            {t("Créer un nouveau compte")}
          </Button>
        </FooterAuth>
      </Content>
    </Container>
  )
}

export const RegisterPending = () => {
  const { t } = useTranslation()

  return (
    <Container>
      <section>
        <p>
          {t(
            "Votre demande d'inscription a bien été envoyée. Vous recevrez un email sous peu contenant un lien qui vous permettra d'activer votre compte afin de pouvoir vous connecter."
          )}
        </p>
      </section>

      <footer>
        <Button
          priority="secondary"
          iconId="ri-arrow-left-line"
          linkProps={{ to: "/" }}
        >
          {t("Retour")}
        </Button>
      </footer>
    </Container>
  )
}
