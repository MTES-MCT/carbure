import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { TextInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { Form, useForm } from "common/components/form2"
import { Text } from "common/components/text"
import { Content, DialogContainer, Section } from "auth/layouts/container"
import { ROUTE_URLS } from "common/utils/routes"
import * as api from "../../api"

type ActivateRequestForm = {
  email?: string
}

type ActivateRequestProps = {
  onClose?: () => void
}

export const ActivateRequest = ({ onClose }: ActivateRequestProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const location = useLocation()
  const email = (location.state as ActivateRequestForm | null)?.email
  const [sent, setSent] = useState(false)

  const { value, bind } = useForm<ActivateRequestForm>({
    email: email ?? "",
  })

  const requestActivationLink = useMutation(api.requestActivateAccount, {
    onSuccess: () => setSent(true),
    onError: () => {
      notify(t("Le lien n'a pas pu être envoyé !"), { variant: "danger" })
    },
  })

  const close = onClose ?? (() => navigate(ROUTE_URLS.AUTH.REGISTER))

  if (sent) {
    return (
      <DialogContainer
        onClose={() => navigate(ROUTE_URLS.AUTH.LOGIN)}
        title={t("Vérifiez votre boîte mail")}
      >
        <Content>
          <Section>
            <Text>
              {t(
                "Si un compte en attente d'activation correspond à cette adresse, un nouveau lien vient de lui être envoyé. Pensez à vérifier vos courriers indésirables."
              )}
            </Text>
          </Section>
          <Button asideX onClick={() => navigate(ROUTE_URLS.AUTH.LOGIN)}>
            {t("Retour à la connexion")}
          </Button>
        </Content>
      </DialogContainer>
    )
  }

  return (
    <DialogContainer onClose={close} title={t("Renvoyer le lien d’activation")}>
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
