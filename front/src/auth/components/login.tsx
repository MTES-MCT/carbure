import React from "react"
import cl from "clsx"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import Button from "common-v2/components/button"
import Form, { useForm } from "common-v2/components/form"
import { Mail, Lock, UserCheck, Return } from "common-v2/components/icons"
import { TextInput } from "common-v2/components/input"
import { useMatch } from "react-router-dom"
import { Link } from "react-router-dom"
import { Overlay, Panel } from "common-v2/components/scaffold"
import marianne from "carbure/assets/images/Marianne.svg"
import css from "./auth.module.css"
import { useNotify } from "common-v2/components/notifications"
import { useMutation } from "common-v2/hooks/async"
import * as api from "../api"

const Login = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({
    email: "" as string | undefined,
    password: "" as string | undefined,
  })

  const login = useMutation(api.login, {
    onSuccess: () => {
      notify(t("Un code vient de vous être envoyé"), { variant: "success" })
      navigate("otp")
    },
    onError: () => {
      notify(t("La connexion a échoué"), { variant: "danger" })
    },
  })

  return (
    <Container>
      <header>
        <Logo />
      </header>

      <section>
        <Switcher />
      </section>

      <section>
        <Form
          id="login"
          onSubmit={() => login.execute(value.email!, value.password!)}
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
            icon={Lock}
            type="password"
            label={t("Mot de passe")}
            {...bind("password")}
          />
          <Button
            variant="link"
            label={t("J'ai oublié mon mot de passe")}
            to="../reset-password-request"
            className={css.formLink}
          />
        </Form>
      </section>

      <footer>
        <Button
          center
          loading={login.loading}
          disabled={!value.email || !value.password}
          variant="primary"
          icon={UserCheck}
          submit="login"
          label={t("Se connecter au compte")}
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

export const Container = ({ children }: { children: React.ReactNode }) => (
  <Overlay className={css.auth}>
    <Panel className={css.panel}>{children}</Panel>
  </Overlay>
)

export const Switcher = () => {
  const { t } = useTranslation()
  const match = useMatch("auth/:focus")
  const isLogin = match?.params.focus === "login"
  return (
    <div className={css.switcher}>
      <Link to="../login" className={cl(isLogin && css.active)}>
        {"→ "}
        {t("Connexion")}
      </Link>
      <Link to="../register" className={cl(!isLogin && css.active)}>
        {"→ "}
        {t("Inscription")}
      </Link>
    </div>
  )
}

export const Logo = () => (
  <Link to="/" className={css.logo}>
    <img src={marianne} alt="marianne logo" />
    <h1>CarbuRe</h1>
  </Link>
)

export default Login
