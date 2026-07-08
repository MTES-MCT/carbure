import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { Form, useForm } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"
import {
  Container,
  Content,
  DialogContainer,
  DialogContainerSpacing,
  Section,
} from "auth/layouts/container"
import { Title } from "common/components/title"
import {
  PasswordInput,
  usePasswordValidation,
} from "auth/components/password-input"
import { ActivateRequest } from "./activate"
import { Text } from "common/components/text"
import Alert from "@codegouvfr/react-dsfr/Alert"
import { ROUTE_URLS } from "common/utils/routes"
import HashRoute from "common/components/hash-route"

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
      navigate(ROUTE_URLS.AUTH.REGISTER_PENDING)
    },

    onError: (error) => {
      notifyError(error)
    },
  })

  const { isValid } = usePasswordValidation(
    value.password,
    value.repeatPassword
  )

  const handleRegister = () => {
    if (!isValid) return

    register.execute(
      value.email!,
      value.name!,
      value.password!,
      value.repeatPassword!
    )
  }

  return (
    <Container>
      <Title is="h1" as="h3" style={{ textAlign: "center" }}>
        {t("Inscription")}
      </Title>

      <Content>
        <Form id="register" gap="sm" onSubmit={handleRegister}>
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
            autoComplete="new-password"
            required
          />
          <PasswordInput
            label={t("Répéter le mot de passe")}
            value={value.repeatPassword}
            onChange={(v) => setField("repeatPassword", v)}
            confirm={value.password}
            autoComplete="new-password"
            required
          />
        </Form>

        <Button
          customPriority="link"
          linkProps={{ to: ROUTE_URLS.AUTH.ACTIVATE_REQUEST }}
          center
        >
          {t("Je n'ai pas reçu le lien d'activation")}
        </Button>
        <Button
          loading={register.loading}
          type="submit"
          nativeButtonProps={{ form: "register" }}
          asideX
        >
          {t("Créer un nouveau compte")}
        </Button>
      </Content>
      <HashRoute path="pending" element={<RegisterPending />} />
      <HashRoute path="activate-request" element={<ActivateRequest />} />
    </Container>
  )
}

export const RegisterPending = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <DialogContainer onClose={() => navigate(-1)}>
      <Content>
        <Section>
          <Alert
            severity="success"
            description={t("Le compte a bien été créé !")}
            small
            closable
          />
          <Text>
            {t(
              "Votre demande d'inscription a bien été envoyée. Vous recevrez un email sous peu contenant un lien qui vous permettra d'activer votre compte afin de pouvoir vous connecter."
            )}
          </Text>
          <DialogContainerSpacing />
        </Section>
      </Content>
    </DialogContainer>
  )
}
