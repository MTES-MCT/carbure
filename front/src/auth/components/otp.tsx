import Button from "common/components/button"
import { useTranslation } from "react-i18next"
import { useNavigate, useSearchParams } from "react-router-dom"
import Form, { useForm } from "common/components/form"
import { Lock, Return, UserCheck } from "common/components/icons"
import { TextInput } from "common/components/input"
import { Container } from "./login"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"
import { useEffect } from "react"

const OTP = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

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

  // if a code is specified in the url, automatically call the api with it
  const execVerifyOTP = verifyOTP.execute
  useEffect(() => {
    if (searchParams.has("token")) {
      execVerifyOTP(searchParams.get("token")!)
    }
  }, [searchParams, execVerifyOTP])

  return (
    <Container>
      <section>
        <p>
          {t(
            "Un code à 6 chiffres vient d'être envoyé à l'adresse email spécifiée, veuillez l'entrer dans le champ ci-dessous pour confirmer votre connexion :"
          )}
        </p>
      </section>

      <section>
        <Form id="otp" onSubmit={() => verifyOTP.execute(value.otp!)}>
          <TextInput
            autoFocus
            variant="solid"
            icon={Lock}
            label={t("Code reçu par email")}
            {...bind("otp")}
          />
        </Form>
      </section>

      <section>
        <p>
          {t(
            "Notez qu'il vous faudra peut-être patienter quelques minutes avant que l'email n'arrive dans votre boite de réception."
          )}
        </p>
        <Button
          variant="link"
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
