import Button from "common/components/button"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import Form, { useForm } from "common/components/form"
import { Mail, Lock, Return, UserAdd, User } from "common/components/icons"
import { TextInput } from "common/components/input"
import { Container, Switcher } from "./login"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"
import { AxiosError } from "axios"
import { Api } from "common/services/api"

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

    onError: (error) => {
      const errors = []
      const errorData =
        (error as AxiosError<Api<any>>).response?.data?.data ?? {}

      for (const field in errorData) {
        const fieldErrors = errorData[field]
        errors.push(...fieldErrors)
      }

      const content = (
        <>
          <div style={{ marginBottom: 8 }}>
            {t("Le compte n'a pas pu être créé !")}
          </div>
          <ul>
            {errors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </>
      )

      notify(content, { variant: "danger" })
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
            autoFocus
            variant="solid"
            icon={Mail}
            type="email"
            label={t("Adresse email")}
            {...bind("email")}
          />
          <TextInput
            variant="solid"
            placeholder="Jean-François CHAMPOLLION"
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
            error={!isPassOk ? t("Les mots de passe ne correspondent pas") : undefined} // prettier-ignore
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
