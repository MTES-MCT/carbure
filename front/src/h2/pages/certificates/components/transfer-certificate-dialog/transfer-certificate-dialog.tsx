import { useTranslation } from "react-i18next"

import { Alert } from "common/components/alert2"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form } from "common/components/form2"
import { formatUnitOnly } from "common/utils/formatters"
import { TiruertLiableAutocomplete } from "common/molecules/tiruert-liable-autocomplete"
import { ActionDecimalInput } from "traceability/components/action-decimal-input"
import { Action } from "traceability/types"
import { formatUnitActionDecimal } from "traceability/utils/formatters"
import { useTransferCertificateDialog } from "./transfer-certificate-dialog.hooks"

const FORM_ID = "transfer-certificate-form"

export type TransferCertificateDialogProps = {
  action: Action
  onClose: () => void
}

export const TransferCertificateDialog = ({
  action,
  onClose,
}: TransferCertificateDialogProps) => {
  const { t } = useTranslation()
  const dialog = useTransferCertificateDialog(action, onClose)
  const quantity = dialog.form.bind("quantity")

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Certificat de cession")}</Dialog.Title>}
      footer={
        <Button
          type="submit"
          priority="primary"
          loading={dialog.loading}
          nativeButtonProps={{ form: FORM_ID }}
        >
          {t("Émettre un certificat de cession")}
        </Button>
      }
      size="medium"
    >
      <Form id={FORM_ID} form={dialog.form} onSubmit={dialog.transfer}>
        {dialog.parent && dialog.lotPath && (
          <Button
            customPriority="link"
            linkProps={{ to: dialog.lotPath, target: "_blank" }}
          >
            {t("Certificat lié au lot n°{{id}}", { id: dialog.parent.id })}
          </Button>
        )}

        {dialog.previousMaterial && (
          <Alert
            small
            severity="info"
            description={t(
              "Vous transmettez un certificat pour une quantité de type : {{name}}",
              { name: dialog.previousMaterial.name }
            )}
          />
        )}

        <ActionDecimalInput
          {...quantity}
          required
          min={0.001}
          label={t("Quantité d'énergie")}
          hintText={
            dialog.unit
              ? t("En {{unit}}", { unit: formatUnitOnly(dialog.unit) })
              : undefined
          }
          addon={
            <Button priority="primary" onClick={dialog.setMaxQuantity}>
              {t("Max")}
            </Button>
          }
          state={quantity.state ?? "info"}
          stateRelatedMessage={
            quantity.stateRelatedMessage ??
            t("{{available}} disponible au total", {
              available: dialog.unit
                ? formatUnitActionDecimal(
                    action.quantity_available,
                    dialog.unit
                  )
                : action.quantity_available,
            })
          }
        />
        <ActionDecimalInput
          label={t("Quantité de CO2")}
          hintText={t("En {{unit}}", { unit: "g" })}
          value={dialog.co2}
          disabled
        />
        <TiruertLiableAutocomplete
          label={t("Redevable")}
          required
          {...dialog.form.bind("holder")}
        />
      </Form>
    </Dialog>
  )
}
