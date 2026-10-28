import { Dialog } from "common/components/dialog2"
import { PortalInstance } from "common/components/portal"
import { useTranslation } from "react-i18next"
import { useState } from "react"
import { Button } from "common/components/button2"
import { Form } from "common/components/form2"
import { RadioGroup } from "common/components/inputs2"
import { AgreementRegistrationStatus } from "double-counting/types"
import { getAgreementRegistrationStatusLabel } from "double-counting/formatters"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import * as api from "../../api"

type AgreementDetailsDialogChangeStatusProps = {
  agreementId: number
  initialStatus?: AgreementRegistrationStatus
  onClose: PortalInstance["close"]
  onSuccess: () => void
}

const availableStatuses: AgreementRegistrationStatus[] = [
  AgreementRegistrationStatus.VALID,
  AgreementRegistrationStatus.SUSPENDED,
  AgreementRegistrationStatus.WITHDRAWN,
  AgreementRegistrationStatus.TERMINATED,
]

const AgreementDetailsDialogChangeStatus = ({
  agreementId,
  initialStatus,
  onClose,
  onSuccess,
}: AgreementDetailsDialogChangeStatusProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const entity = useEntity()
  const [selectedStatus, setSelectedStatus] = useState<
    AgreementRegistrationStatus | undefined
  >(initialStatus)

  const updateStatus = useMutation(api.updateDoubleCountingAgreementStatus, {
    invalidates: ["dc-agreement", "dc-agreements", "dc-snapshot"],
    onSuccess: () => {
      notify(t("Le statut a été changé avec succès."), { variant: "success" })
      onClose()
      onSuccess()
    },
    onError: (error) =>
      notifyError(error, t("Impossible de modifier le statut de l'agrément.")),
  })

  const handleConfirm = async () => {
    if (!selectedStatus) return
    await updateStatus.execute(entity.id, agreementId, selectedStatus)
  }

  const loading = updateStatus.loading

  return (
    <Dialog
      onClose={onClose}
      header={
        <>
          <Dialog.Title>{t("Changer le statut")}</Dialog.Title>
          <Dialog.Description>
            {t("Sélectionnez le nouveau statut pour cet agrément.")}
          </Dialog.Description>
        </>
      }
      footer={
        <Button
          type="submit"
          loading={loading}
          nativeButtonProps={{ form: "agreement-change-status-form" }}
        >
          {t("Confirmer")}
        </Button>
      }
    >
      <Form id="agreement-change-status-form" onSubmit={handleConfirm}>
        <RadioGroup
          label={t("Statut")}
          options={availableStatuses.map((status) => ({
            label: getAgreementRegistrationStatusLabel(status, t),
            value: status,
          }))}
          value={selectedStatus}
          onChange={setSelectedStatus}
          required
        />
      </Form>
    </Dialog>
  )
}

export { AgreementDetailsDialogChangeStatus }
