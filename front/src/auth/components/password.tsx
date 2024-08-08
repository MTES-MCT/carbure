import { useTranslation } from "react-i18next"
import Button from "common/components/button"
import { useNavigate } from "react-router-dom"
import Form, { useForm } from "common/components/form"
import { Lock, Mail, Refresh, Return, Save } from "common/components/icons"
import { TextInput } from "common/components/input"
import { Container } from "./login"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"
import { useToken } from "./activate"

export const ResetPasswordRequest = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({
    email: "" as string | undefined,
  })

  const requestPasswordReset = useMutation(api.requestResetPassword, {
    onSuccess: () => {
      notify(t("La demande de changement de mot de passe a été envoyée !"), {
        variant: "success",
      })
      navigate("../reset-password-pending")
    },

    onError: () => {
      notify(t("La demande n'a pas pu être envoyée !"), {
        variant: "danger",
      })
    },
  })

  return (
    <Container>
      <section>
        <p>
          {t(
            "Veuillez renseigner votre adresse email afin que nous vous envoyions les instructions pour réinitialiser votre mot de passe."
          )}
        </p>
      </section>

      <section>
        <Form
          id="reset-password-request"
          onSubmit={() => requestPasswordReset.execute(value.email!)}
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
          loading={requestPasswordReset.loading}
          disabled={!value.email}
          variant="primary"
          icon={Refresh}
          label={t("Demander une réinitialisation")}
          submit="reset-password-request"
        />
        <Button
          center
          variant="secondary"
          icon={Return}
          label={t("Annuler")}
          action={() => navigate("../login")}
        />
      </footer>
    </Container>
  )
}

export const ResetPasswordPending = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <Container>
      <section>
        <p>
          {t(
            "Votre demande de réinitialisation de mot de passe a bien été envoyée. Vous recevrez un email sous peu contenant un lien qui vous permettra de modifier votre mot de passe."
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

export const ResetPassword = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({
    newPassword: "" as string | undefined,
    repeatNewPassword: "" as string | undefined,
  })

  const { uidb64, token } = useToken()

  const resetPassword = useMutation(api.resetPassword, {
    onSuccess: () => {
      notify(t("Le mot de passe a bien été changé !"), { variant: "success" })
      navigate("../login")
    },

    onError: () => {
      notify(t("La modification du mot de passe a échoué !"), {
        variant: "danger",
      })
    },
  })

  const isPassOk = value.newPassword === value.repeatNewPassword

  return (
    <Container>
      <section>
        <p>
          {t(
            "Vous pouvez maintenant modifier votre mot de passe en renseignant les champs ci-dessous"
          )}
        </p>
      </section>

      <section>
        <Form
          id="reset-password"
          onSubmit={() =>
            resetPassword.execute(
              uidb64,
              token,
              value.newPassword!,
              value.repeatNewPassword!
            )
          }
        >
          <TextInput
            autoFocus
            variant="solid"
            icon={Lock}
            type="password"
            label={t("Nouveau mot de passe")}
            {...bind("newPassword")}
          />
          <TextInput
            variant="solid"
            icon={Lock}
            type="password"
            label={t("Répéter le nouveau mot de passe")}
            {...bind("repeatNewPassword")}
            error={!isPassOk ? t("Les mots de passe ne correspondent pas") : undefined} // prettier-ignore
          />
        </Form>
      </section>

      <footer>
        <Button
          center
          loading={resetPassword.loading}
          disabled={
            !isPassOk ||
            !token ||
            !value.newPassword ||
            !value.repeatNewPassword
          }
          variant="primary"
          icon={Save}
          submit="reset-password"
          label={t("Enregistrer le nouveau mot de passe")}
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
