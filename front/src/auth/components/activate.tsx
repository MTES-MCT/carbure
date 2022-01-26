import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useNavigate, useSearchParams } from "react-router-dom"
import { useMutation, useQuery } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import Form, { useForm } from "common-v2/components/form"
import { TextInput } from "common-v2/components/input"
import {
  Loader,
  Mail,
  Refresh,
  Return,
  UserCheck,
} from "common-v2/components/icons"
import Button from "common-v2/components/button"
import { Container } from "./login"
import * as api from "../api"
import css from "./auth.module.css"

export const Activate = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const token = useToken()

  const activate = useQuery(api.activateAccount, {
    key: "activate-account",
    params: [token],
  })

  const isSuccess = activate.status === "success"
  const isError = activate.status === "error"

  return (
    <Container>
      <section>
        {activate.loading && <Loader size={48} className={css.loader} />}
        {isSuccess && (
          <p>
            {t(
              "Votre compte a bien été activé, vous pouvez maintenant vous connecter sur CarbuRe."
            )}
          </p>
        )}
        {isError && (
          <p style={{ color: "var(--red-dark)" }}>
            {t(
              "Une erreur s'est produite lors de l'activation de votre compte, merci de recommencer le processus d'inscription."
            )}
          </p>
        )}
      </section>

      <footer>
        {isSuccess && (
          <Button
            center
            variant="primary"
            icon={UserCheck}
            label={t("Se connecter")}
            action={() => navigate("../login")}
          />
        )}
        {isError && (
          <Button
            center
            variant="warning"
            icon={Refresh}
            label={t("Réessayer de s'inscrire")}
            action={() => navigate("../register")}
          />
        )}
      </footer>
    </Container>
  )
}

export const ActivateRequest = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({
    email: "" as string | undefined,
  })

  const requestActivationLink = useMutation(api.requestActivateAccount, {
    onSuccess: () => {
      notify(t("Le nouveau lien d'activation a été envoyé !"), {
        variant: "success",
      })
      navigate("../reset-password-pending")
    },

    onError: () => {
      notify(t("Lle lien n'a pas pu être envoyé !"), {
        variant: "danger",
      })
    },
  })

  return (
    <Container>
      <section>
        <p>
          {t(
            "Veuillez renseigner votre adresse email afin que nous vous envoyions le lien qui vous permettra d'activer votre compte."
          )}
        </p>
      </section>

      <section>
        <Form
          id="activate-request"
          onSubmit={() => requestActivationLink.execute(value.email!)}
        >
          <TextInput
            variant="solid"
            icon={Mail}
            type="email"
            label={t("Adresse email du compte")}
            {...bind("email")}
          />
        </Form>
      </section>

      <footer>
        <Button
          center
          loading={requestActivationLink.loading}
          disabled={!value.email}
          variant="primary"
          icon={Refresh}
          label={t("Renvoyer le lien d'activation")}
          submit="activate-request"
        />
        <Button
          center
          variant="secondary"
          icon={Return}
          label={t("Annuler")}
          action={() => navigate("../register")}
        />
      </footer>
    </Container>
  )
}

export function useToken() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get("token")

  useEffect(() => {
    if (token === null) {
      navigate("/")
    }
  }, [token, navigate])

  return token
}
