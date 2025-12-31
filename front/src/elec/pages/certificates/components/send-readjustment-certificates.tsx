import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { NumberInput } from "common/components/inputs2"
import { Notice } from "common/components/notice"
import { useTranslation } from "react-i18next"
import { createTransferCertificate } from "../api"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { getTransferErrorLabel } from "../utils"

type SendReadjustmentCertificatesDialogProps = {
  onClose: () => void
  balance: number
  formattedBalance: string
  readjustmentBalance: number
  formattedReadjustmentBalance: string
}

export const SendReadjustmentCertificatesDialog = ({
  onClose,
  balance,
  formattedBalance,
  readjustmentBalance,
  formattedReadjustmentBalance,
}: SendReadjustmentCertificatesDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const form = useForm({
    energy_amount: 0 as number | undefined,
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
      notify(t("Le certificat de réajustement a bien été créé."), {
        variant: "success",
      })
      onClose()
    },

    onError(e) {
      notify(
        t("Le certificat de réajustement n'a pas pu être créé : {{error}}", {
          error: getTransferErrorLabel(e),
        }),
        { variant: "danger" }
      )
    },
  })

  function onSubmit() {
    if (form.value.energy_amount) {
      transferResponse.execute(
        entity.id,
        form.value.energy_amount,
        undefined,
        true
      )
    }
  }

  const max = Math.min(balance, readjustmentBalance)

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>
          {t("Émission de certificat de réajustement")}
        </Dialog.Title>
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
            disabled={!form.value.energy_amount}
            nativeButtonProps={{
              form: "transfer-certificate-form",
            }}
          >
            {t("Émettre le réajustement")}
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
          max={max}
          addon={
            <Button onClick={() => form.setField("energy_amount", max)}>
              {t("Max")}
            </Button>
          }
          {...form.bind("energy_amount")}
        />

        <Notice>
          {t(
            "{{readjustmentBalance}} en excédent, pour {{balance}} d'énergie disponible au total",
            {
              readjustmentBalance: formattedReadjustmentBalance,
              balance: formattedBalance,
            }
          )}
        </Notice>
      </Form>
    </Dialog>
  )
}
