import { Button } from "common/components/button2"
import { useMutation } from "common/hooks/async"
import { acceptTransferCertificate } from "../api"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { Dialog } from "common/components/dialog2"
import { usePortal } from "common/components/portal"
import { useForm } from "common/components/form"
import { useNotify } from "common/components/notifications"
import { DateInput, RadioGroup } from "common/components/inputs2"
import { Form } from "common/components/form2"

type AcceptTransferCertificateProps = {
  id: number
}

export const AcceptTransferCertificate = ({
  id,
}: AcceptTransferCertificateProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  function showDialog() {
    portal((close) => (
      <AcceptTransferCertificateDialog id={id} onClose={close} />
    ))
  }

  return (
    <Button
      iconId="fr-icon-check-line"
      customPriority="success"
      onClick={showDialog}
    >
      {t("Accepter")}
    </Button>
  )
}

type AcceptTransferCertificateDialogProps = {
  id: number
  onClose: () => void
}

const AcceptTransferCertificateDialog = ({
  id,
  onClose,
}: AcceptTransferCertificateDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const entity = useEntity()

  const form = useForm({
    consumptionDate: undefined as string | undefined,
    usedInTiruert: "false",
  })

  const acceptResponse = useMutation(acceptTransferCertificate, {
    invalidates: [
      "elec-transfer-certificates",
      "elec-certificates-snapshot",
      "transfer-certificate-details",
      "years",
    ],
    onSuccess() {
      notify(t("Le certificat a bien été accepté"), { variant: "success" })
      onClose()
    },
    onError() {
      notify(t("Le certificat n'a pas pu être accepté"), { variant: "danger" })
      onClose()
    },
  })

  function onAccept() {
    acceptResponse.execute(
      entity.id,
      id,
      form.value.usedInTiruert,
      form.value.consumptionDate
    )
  }

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Accepter le certificat")}</Dialog.Title>}
      footer={
        <>
          <Button priority="secondary" onClick={onClose}>
            {t("Annuler")}
          </Button>
          <Button
            iconId="fr-icon-check-line"
            type="submit"
            customPriority="success"
            nativeButtonProps={{ form: "accept-elec-transfer-form" }}
          >
            {t("Confirmer")}
          </Button>
        </>
      }
    >
      <Form id="accept-elec-transfer-form" onSubmit={onAccept}>
        <RadioGroup
          {...form.bind("usedInTiruert")}
          label={t(
            "Ce certificat a-t-il été consommé dans le cadre d'une déclaration TIRUERT ?"
          )}
          options={[
            {
              value: "false",
              label: t("Ne concerne pas encore une déclaration"),
            },
            {
              value: "true",
              label: t("Concerne une déclaration TIRUERT"),
            },
          ]}
        />

        {form.value.usedInTiruert === "true" && (
          <DateInput
            required
            type="date"
            label={t("J'indique la date de déclaration")}
            {...form.bind("consumptionDate")}
            style={{ marginTop: "var(--spacing-m)" }}
          />
        )}
      </Form>
    </Dialog>
  )
}
