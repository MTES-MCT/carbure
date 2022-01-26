import Button from "common-v2/components/button"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import Form, { useForm } from "common-v2/components/form"
import { Lock, Return, UserCheck } from "common-v2/components/icons"
import { TextInput } from "common-v2/components/input"
import { Container, Logo } from "./login"
import { useNotify } from "common-v2/components/notifications"
import { useMutation } from "common-v2/hooks/async"
import * as api from "../api"

const OTP = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()

  const { value, bind } = useForm({
    otp: "" as string | undefined,
  })

  const verifyOTP = useMutation(api.verifyOTP, {
    invalidates: ["user-settings"],

    onSuccess: () => {
      notify(t("Vous êtes connecté !"), { variant: "success" })
      navigate("/")
    },

    onError: () => {
      notify(t("La vérification du code a échoué !"), { variant: "danger" })
    },
  })

  const requestOTP = useMutation(api.requestOTP, {
    onSuccess: () => {
      notify(t("Un nouveau code vous a été envoyé !"), { variant: "success" })
    },

    onError: () => {
      notify(t("Le code n'a pas pu être envoyé !"), { variant: "danger" })
    },
  })

  return (
    <Container>
      <header>
        <Logo />
      </header>

      <section>
        <p>
          {t(
            "Un code à 6 chiffres vient de vous être envoyé à l'adresse email spécifiée, veuillez l'entrer dans le champ ci-dessous pour confirmer votre connexion :"
          )}
        </p>
      </section>

      <section>
        <Form id="otp" onSubmit={() => verifyOTP.execute(value.otp!)}>
          <TextInput
            variant="solid"
            icon={Lock}
            type="password"
            label={t("Code reçu par email")}
            {...bind("otp")}
          />
        </Form>
      </section>

      <section>
        <p>
          {t(
            "Notez qu'il vous faudra peut-être patienter quelques minutes avant que l'email n'arrive dans votre boite mail."
          )}
        </p>
        <Button
          variant="link"
          loading={requestOTP.loading}
          label={t("Renvoyer le code à l'adresse indiquée")}
          action={() => requestOTP.execute()}
        />
      </section>

      <footer>
        <Button
          center
          loading={verifyOTP.loading}
          disabled={!value.otp}
          variant="primary"
          icon={UserCheck}
          submit="otp"
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

export default OTP
