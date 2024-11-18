import React from "react"
import cl from "clsx"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import Button from "common/components/button"
import Form, { useForm } from "common/components/form"
import { Mail, Lock, UserCheck, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useMatch } from "react-router-dom"
import { Link } from "react-router-dom"
import { Overlay, Panel } from "common/components/scaffold"
import marianne from "common/assets/images/Marianne.svg"
import css from "./auth.module.css"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"

const Login = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({
    username: "" as string | undefined,
    password: "" as string | undefined,
  })

  const login = useMutation(api.login, {
    onSuccess: () => {
      notify(t("Un code vient de vous être envoyé"), { variant: "success" })
      api.requestOTP()
      navigate("../otp")
    },
    onError: () => {
      notify(t("La connexion a échoué"), { variant: "danger" })
    },
  })

  return (
    <Container>
      <section>
        <Switcher />
      </section>

      <section>
        <Form
          id="login"
          onSubmit={() => login.execute(value.username!, value.password!)}
        >
          <TextInput
            autoFocus
            variant="solid"
            icon={Mail}
            type="email"
            label={t("Adresse email")}
            {...bind("username")}
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
          />
        </Form>
      </section>

      <footer>
        <Button
          center
          loading={login.loading}
          disabled={!value.username || !value.password}
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
    <Panel className={css.panel}>
      <header>
        <Logo />
      </header>
      {children}
    </Panel>
  </Overlay>
)

export const Switcher = () => {
  const { t } = useTranslation()
  const match = useMatch("auth/:focus")
  const isLogin = match?.params.focus === "login"
  const isRegister = match?.params.focus === "register"
  return (
    <div className={css.switcher}>
      <Link to="../login" className={cl(isLogin && css.active)}>
        {"→ "}
        {t("Connexion")}
      </Link>
      <Link to="../register" className={cl(isRegister && css.active)}>
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
