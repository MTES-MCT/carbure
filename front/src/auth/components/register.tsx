import Button from "common-v2/components/button"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import Form, { useForm } from "common-v2/components/form"
import { Mail, Lock, Return, UserAdd, User } from "common-v2/components/icons"
import { TextInput } from "common-v2/components/input"
import { Container, Switcher } from "./login"
import { useNotify } from "common-v2/components/notifications"
import { useMutation } from "common-v2/hooks/async"
import * as api from "../api"

export const Register = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({
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

    onError: () => {
      notify(t("Le compte n'a pas pu être créé !"), { variant: "danger" })
    },
  })

  const isPassOk = value.password === value.repeatPassword

  return (
    <Container>
      <section>
        <Switcher />
      </section>

      <section>
        <Form
          id="register"
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
            variant="solid"
            icon={Mail}
            type="email"
            label={t("Adresse email")}
            {...bind("email")}
          />
          <TextInput
            variant="solid"
            placeholder="Jean-Pierre CHAMPOLLION"
            icon={User}
            label={t("Nom")}
            {...bind("name")}
          />
          <TextInput
            variant="solid"
            icon={Lock}
            type="password"
            label={t("Mot de passe")}
            {...bind("password")}
          />
          <TextInput
            variant="solid"
            icon={Lock}
            type="password"
            label={t("Répéter le mot de passe")}
            {...bind("repeatPassword")}
            error={!isPassOk ? t("Les mots de passe de correspondent pas") : undefined} // prettier-ignore
          />
          <Button
            variant="link"
            label={t("Je n'ai pas reçu le lien d'activation")}
            to="../activate-request"
          />
        </Form>
      </section>

      <footer>
        <Button
          center
          loading={register.loading}
          disabled={
            !isPassOk ||
            !value.email ||
            !value.password ||
            !value.repeatPassword
          }
          variant="primary"
          icon={UserAdd}
          submit="register"
          label={t("Créer un nouveau compte")}
        />
        <Button
          center
          variant="secondary"
          icon={Return}
          label={t("Annuler")}
          action={() => navigate("/")}
        />
      </footer>
    </Container>
  )
}

export const RegisterPending = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

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
          center
          variant="secondary"
          icon={Return}
          label={t("Retour")}
          action={() => navigate("/")}
        />
      </footer>
    </Container>
  )
}
