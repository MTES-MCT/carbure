import Button from "common-v2/components/button"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import Form, { useForm } from "common-v2/components/form"
import { Mail, Lock, Return, UserAdd } from "common-v2/components/icons"
import { TextInput } from "common-v2/components/input"
import { Container, Logo, Switcher } from "./login"

const Register = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const { value, bind } = useForm({
    email: "" as string | undefined,
    password: "" as string | undefined,
    repeatPassword: "" as string | undefined,
  })

  const isPassOk = value.password === value.repeatPassword

  return (
    <Container>
      <header>
        <Logo />
      </header>

      <section>
        <Switcher />
      </section>

      <section>
        <Form id="register">
          <TextInput
            variant="solid"
            icon={Mail}
            type="email"
            label={t("Adresse email")}
            {...bind("email")}
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
        </Form>
      </section>

      <footer>
        <Button
          center
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

export default Register
