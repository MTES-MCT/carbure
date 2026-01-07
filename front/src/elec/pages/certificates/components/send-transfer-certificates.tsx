import { Autocomplete } from "common/components/autocomplete2"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { NumberInput } from "common/components/inputs2"
import { Notice } from "common/components/notice"
import { usePortal } from "common/components/portal"
import { EntityPreview } from "common/types"
import { useTranslation } from "react-i18next"
import { createTransferCertificate, getClients } from "../api"
import useEntity from "common/hooks/entity"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { getTransferErrorLabel } from "../utils"

export interface SendTransferCertificatesProps {
  balance: number
  formattedBalance: string
}

export const SendTransferCertificates = ({
  balance,
  formattedBalance,
}: SendTransferCertificatesProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  function showDialog() {
    portal((close) => (
      <SendTransferCertificatesDialog
        onClose={close}
        balance={balance}
        formattedBalance={formattedBalance}
      />
    ))
  }

  return (
    <Button iconId="fr-icon-draft-fill" asideX onClick={showDialog}>
      {t("Émettre des certificats de cession")}
    </Button>
  )
}

type SendTransferCertificatesDialogProps = {
  onClose: () => void
  balance: number
  formattedBalance: string
}

const SendTransferCertificatesDialog = ({
  onClose,
  balance,
  formattedBalance,
}: SendTransferCertificatesDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const form = useForm({
    energy_amount: 0 as number | undefined,
    client: undefined as EntityPreview | undefined,
  })

  const transferResponse = useMutation(createTransferCertificate, {
    invalidates: [
      "elec-provision-certificates",
      "elec-transfer-certificates",
      "elec-certificates-snapshot",
      "elec-provision-certificate-balance",
      "years",
    ],

    onSuccess() {
      notify(t("Le certificat de cession a bien été créé."), {
        variant: "success",
      })
      onClose()
    },

    onError(e) {
      notify(
        t("Le certificat de cession n'a pas pu être créé : {{error}}", {
          error: getTransferErrorLabel(e),
        }),
        { variant: "danger" }
      )
    },
  })

  function onSubmit() {
    if (form.value.energy_amount && form.value.client) {
      transferResponse.execute(
        entity.id,
        form.value.energy_amount,
        form.value.client.id
      )
    }
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>{t("Émission de certificat de cession")}</Dialog.Title>
      }
      footer={
        <>
          <Button priority="secondary" onClick={onClose}>
            Annuler
          </Button>
          <Button
            iconId="fr-icon-send-plane-fill"
            type="submit"
            loading={transferResponse.loading}
            disabled={!form.value.energy_amount || !form.value.client}
            nativeButtonProps={{
              form: "transfer-certificate-form",
            }}
          >
            {t("Émettre le certificat")}
          </Button>
        </>
      }
    >
      <Form id="transfer-certificate-form" onSubmit={onSubmit}>
        <p>
          {t(
            "Les quantités d'énergies seront prélevées sur la base de vos certificats de fourniture, en commençant par les plus anciens."
          )}
        </p>

        <NumberInput
          required
          label={t("Quantité d'énergie (MWh)")}
          max={balance}
          min={0.01}
          step={0.01}
          addon={
            <Button onClick={() => form.setField("energy_amount", balance)}>
              {t("Max")}
            </Button>
          }
          {...form.bind("energy_amount")}
        />

        <Notice>
          {t("{{balance}} d'énergie disponible au total", {
            balance: formattedBalance,
          })}
        </Notice>

        <Autocomplete
          required
          label={t("Redevable")}
          getOptions={(search) => getClients(entity.id, search)}
          normalize={normalizeEntityPreview}
          {...form.bind("client")}
        />
      </Form>
    </Dialog>
  )
}
