import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { Button } from "common/components/button2"
import { Form, useForm } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { Container, Content, FooterAuth, Section } from "auth/layouts/container"
import { Title } from "common/components/title"
import { PasswordInput } from "auth/components/password-input"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"
import { ROUTE_URLS } from "common/utils/routes"
import { Divider } from "common/components/divider"

const Login = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind, setField } = useForm({
    username: "" as string | undefined,
    password: "" as string | undefined,
  })

  const login = useMutation(api.login, {
    onSuccess: () => {
      notify(t("Un code vient de vous être envoyé"), { variant: "success" })
      api.requestOTP()
      navigate(ROUTE_URLS.AUTH.OTP)
    },
    onError: (error) => {
      let errorMessage = t("La connexion a échoué")
      if (
        (error as any).data &&
        (error as any).data.message === "Account not activated"
      ) {
        errorMessage = t(
          "Votre compte n'est pas activé. Merci de cliquer sur le lien de réactivation pour activer votre compte."
        )
      }
      notify(errorMessage, { variant: "danger" })
    },
  })

  return (
    <Container>
      <Title is="h1" as="h3" style={{ textAlign: "center" }}>
        {t("Connexion")}
      </Title>

      <Content>
        <Form
          id="login"
          gap="sm"
          onSubmit={() => login.execute(value.username!, value.password!)}
        >
          <TextInput
            autoFocus
            type="email"
            label={t("Adresse email")}
            {...bind("username")}
            required
          />
          <div>
            <PasswordInput
              label={t("Mot de passe")}
              value={value.password}
              onChange={(v) => setField("password", v)}
              messages={[]}
              autoComplete="current-password"
              required
            />
            <Button
              customPriority="link"
              linkProps={{ to: ROUTE_URLS.AUTH.RESET_PASSWORD_REQUEST }}
              center
            >
              {t("Mot de passe oublié ?")}
            </Button>
          </div>
        </Form>
        <Section gap="lg">
          <Button
            customPriority="link"
            linkProps={{ to: ROUTE_URLS.AUTH.ACTIVATE_REQUEST }}
            center
          >
            {t("Je n'ai pas reçu le lien d'activation")}
          </Button>
          <Button
            customPriority="link"
            linkProps={{ to: ROUTE_URLS.AUTH.ACTIVATE_REQUEST }}
            center
          >
            {t("Cliquez ici pour activer votre compte.")}
          </Button>
        </Section>

        <FooterAuth>
          <Button priority="secondary" linkProps={{ to: ROUTE_URLS.HOME }}>
            {t("Annuler")}
          </Button>
          <Button
            loading={login.loading}
            type="submit"
            nativeButtonProps={{ form: "login" }}
          >
            {t("Se connecter")}
          </Button>
        </FooterAuth>
        <Divider />
        <Section>
          <Title is="h4" as="h5" style={{ textAlign: "center" }}>
            {t("Vous n'avez pas de compte ?")}
          </Title>
          <Button
            priority="secondary"
            linkProps={{ to: ROUTE_URLS.AUTH.REGISTER }}
            center
          >
            {t("S'inscrire")}
          </Button>
        </Section>
      </Content>
    </Container>
  )
}

export default Login
