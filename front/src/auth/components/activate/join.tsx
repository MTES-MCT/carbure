import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { Form, useForm } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { useNotifyError } from "common/components/notifications"
import { useMutation, useQuery } from "common/hooks/async"
import {
  PasswordInput,
  usePasswordValidation,
} from "auth/components/password-input"
import * as api from "../../api"
import {
  ACTIVATION_FAILED,
  ActivationLayout,
  ActivationScreen,
  apiMessage,
  useActivationLink,
} from "./activation-link"

export const Join = () => {
  const content = useJoin()
  return <ActivationLayout {...content} />
}

function useJoin(): ActivationScreen {
  const { t } = useTranslation()
  const { uidb64, token, activated, invalidLink } = useActivationLink()
  const [done, setDone] = useState(false)
  const [linkRejected, setLinkRejected] = useState(false)
  const link = useQuery(api.checkActivateProfile, {
    key: "check-activate-profile",
    params: [uidb64, token],
  })

  if (done) return activated

  if (link.loading) {
    return { success: false, loading: true, title: t("Activez votre compte") }
  }

  if (link.status === "error" || linkRejected) return invalidLink

  return {
    success: false,
    title: t("Activez votre compte"),
    message: t("Indiquez votre nom et choisissez un mot de passe."),
    form:
      uidb64 && token ? (
        <JoinForm
          uidb64={uidb64}
          token={token}
          onSuccess={() => setDone(true)}
          onLinkRejected={() => setLinkRejected(true)}
        />
      ) : undefined,
  }
}

function JoinForm({
  uidb64,
  token,
  onSuccess,
  onLinkRejected,
}: {
  uidb64: string
  token: string
  onSuccess: () => void
  onLinkRejected: () => void
}) {
  const { t } = useTranslation()
  const notifyError = useNotifyError()
  const { value, bind } = useForm({
    name: "" as string | undefined,
    password: "" as string | undefined,
    repeatPassword: "" as string | undefined,
  })
  const { isValid } = usePasswordValidation(
    value.password,
    value.repeatPassword
  )
  const activateProfile = useMutation(api.activateProfile, {
    onSuccess: () => onSuccess(),
    onError: (error) => {
      if (apiMessage(error) === ACTIVATION_FAILED) {
        onLinkRejected()
        return
      }
      notifyError(error)
    },
  })

  return (
    <Form
      id="join"
      gap="sm"
      onSubmit={() => {
        if (!isValid || !value.name) return
        activateProfile.execute(
          uidb64,
          token,
          value.name,
          value.password!,
          value.repeatPassword!
        )
      }}
    >
      <TextInput
        autoFocus
        placeholder="Jean-François CHAMPOLLION"
        label={t("Nom")}
        {...bind("name")}
        required
      />
      <PasswordInput
        label={t("Mot de passe")}
        {...bind("password")}
        autoComplete="new-password"
        required
      />
      <PasswordInput
        label={t("Répéter le mot de passe")}
        {...bind("repeatPassword")}
        confirm={value.password}
        autoComplete="new-password"
        required
      />
      <Button
        loading={activateProfile.loading}
        disabled={!value.name || !isValid}
        type="submit"
        nativeButtonProps={{ form: "join" }}
        asideX
      >
        {t("Activer mon compte")}
      </Button>
    </Form>
  )
}
