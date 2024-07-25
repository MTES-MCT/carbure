import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import {
  createSearchParams,
  useNavigate,
  useSearchParams,
} from "react-router-dom"
import { useMutation, useQuery } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import Form, { useForm } from "common/components/form"
import { TextInput } from "common/components/input"
import {
  Loader,
  Mail,
  Refresh,
  Return,
  UserCheck,
} from "common/components/icons"
import Button from "common/components/button"
import { Container } from "./login"

import * as api from "../api"
import css from "./auth.module.css"

export const Activate = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { uidb64, token } = useToken()

  const activate = useQuery(api.activateAccount, {
    key: "activate-account",
    params: [uidb64, token],
  })

  const isSuccess = activate.status === "success"
  const isError = activate.status === "error"
  const isUserInvited = searchParams.get("invite")

  const activatedMessage = isUserInvited
    ? t(
        "Votre compte a bien été activé, vous pouvez maintenant définir votre mot de passe."
      )
    : t(
        "Votre compte a bien été activé, vous pouvez maintenant vous connecter sur CarbuRe."
      )

  const userInvitedSearchParams = createSearchParams({
    uidb64: uidb64 || "",
    token: activate.result?.data.token || "",
  })

  return (
    <Container>
      <section>
        {activate.loading && <Loader size={48} className={css.loader} />}
        {isSuccess && <p>{activatedMessage}</p>}
        {isError && (
          <p style={{ color: "var(--red-dark)" }}>
            {t(
              "Une erreur s'est produite lors de l'activation de votre compte, merci de recommencer le processus d'inscription."
            )}
          </p>
        )}
      </section>

      <footer>
        {isUserInvited && (
          <Button
            center
            variant="primary"
            icon={UserCheck}
            label={t("Définir mon mot de passe")}
            to={{
              pathname: "../reset-password",
              search: userInvitedSearchParams.toString(),
            }}
          />
        )}
        {isSuccess && !isUserInvited && (
          <Button
            center
            variant="primary"
            icon={UserCheck}
            label={t("Se connecter")}
            action={() => navigate("../login")}
          />
        )}
        {isError && !isUserInvited && (
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
      navigate("../register-pending")
    },

    onError: () => {
      notify(t("Le lien n'a pas pu être envoyé !"), {
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
            autoFocus
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

  const uidb64 = searchParams.get("uidb64") ?? undefined
  const token = searchParams.get("token") ?? undefined

  useEffect(() => {
    if (uidb64 === undefined || token === undefined) {
      navigate("/")
    }
  }, [uidb64, token, navigate])

  return { uidb64, token }
}
