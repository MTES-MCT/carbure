import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { TextInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { Form, useForm } from "common/components/form2"
import { Content, DialogContainer, Section } from "auth/layouts/container"
import { ROUTE_URLS } from "common/utils/routes"
import * as api from "../../api"

type ActivateRequestForm = {
  email?: string
}

export const ActivateRequest = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const location = useLocation()
  const email = (location.state as ActivateRequestForm | null)?.email

  const { value, bind } = useForm<ActivateRequestForm>({
    email: email ?? "",
  })

  const requestActivationLink = useMutation(api.requestActivateAccount, {
    onSuccess: () => {
      notify(
        t(
          "Si ce compte existe, un nouveau lien d'activation vous a été envoyé"
        ),
        { variant: "success" }
      )
      navigate(ROUTE_URLS.AUTH.REGISTER_PENDING)
    },

    onError: () => {
      notify(t("Le lien n'a pas pu être envoyé !"), { variant: "danger" })
    },
  })

  return (
    <DialogContainer
      onClose={() => navigate(ROUTE_URLS.AUTH.REGISTER)}
      title={t("Renvoyer le lien d’activation")}
    >
      <Content>
        <Section>
          {t(
            "Veuillez renseigner votre adresse email afin que nous vous envoyions le lien qui vous permettra d'activer votre compte."
          )}

          <Form
            id="activate-request"
            onSubmit={() => requestActivationLink.execute(value.email!)}
          >
            <TextInput
              autoFocus
              type="email"
              label={t("Adresse email du compte")}
              {...bind("email")}
              required
            />
          </Form>
        </Section>
        <Button
          loading={requestActivationLink.loading}
          type="submit"
          nativeButtonProps={{ form: "activate-request" }}
          asideX
        >
          {t("Renvoyer le lien d'activation")}
        </Button>
      </Content>
    </DialogContainer>
  )
}
