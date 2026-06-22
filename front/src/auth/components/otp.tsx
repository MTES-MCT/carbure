import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { useNavigate, useSearchParams } from "react-router-dom"
import { Form, useForm } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { Container, Content, FooterAuth, Section } from "auth/layouts/container"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "../api"
import { useEffect } from "react"
import { HttpError } from "common/services/api-fetch"
import { Text } from "common/components/text"

const OTP = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const { value, bind } = useForm({ otp: "" as string | undefined })

  const verifyOTP = useMutation(api.verifyOTP, {
    invalidates: ["user-settings"],

    onSuccess: () => {
      notify(t("Vous êtes connecté !"), { variant: "success" })
      navigate("/")
    },

    onError: (error) => {
      const errorData = (error as HttpError)?.data

      for (const field in errorData) {
        notify(errorData[field], { variant: "danger" })
      }
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
      <Content>
        <Section>
          <Text>
            {t(
              "Un code à 6 chiffres vient d'être envoyé à l'adresse email spécifiée, veuillez l'entrer dans le champ ci-dessous pour confirmer votre connexion :"
            )}
          </Text>

          <Form id="otp" onSubmit={() => verifyOTP.execute(value.otp!)}>
            <TextInput
              autoFocus
              label={t("Code reçu par email")}
              {...bind("otp")}
              required
            />
          </Form>
        </Section>

        <Section>
          <Text>
            {t(
              "Notez qu'il vous faudra peut-être patienter quelques minutes avant que l'email n'arrive dans votre boite de réception."
            )}
          </Text>
          <Button
            customPriority="link"
            onClick={() => requestOTP.execute()}
            center
          >
            {t("Renvoyer le code à l'adresse indiquée")}
          </Button>
        </Section>

        <FooterAuth>
          <Button onClick={() => navigate("/")} priority="secondary">
            {t("Annuler")}
          </Button>
          <Button
            loading={verifyOTP.loading}
            type="submit"
            nativeButtonProps={{ form: "otp" }}
          >
            {t("Se connecter au compte")}
          </Button>
        </FooterAuth>
      </Content>
    </Container>
  )
}

export default OTP
