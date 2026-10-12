import { Dialog } from "common/components/dialog2"
import { PortalInstance } from "common/components/portal"
import { useTranslation } from "react-i18next"
import { useState } from "react"
import { Button } from "common/components/button2"
import { RadioGroup } from "common/components/inputs2"
import { AgreementRegistrationStatus } from "double-counting/types"
import { getAgreementRegistrationStatusLabel } from "double-counting/formatters"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import * as api from "../../api"

type AgreementDetailsDialogChangeStatusProps = {
  agreementIds: number[]
  bulk?: boolean
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
  agreementIds,
  bulk = false,
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
  >(bulk ? AgreementRegistrationStatus.VALID : initialStatus)

  const updateStatuses = useMutation(api.updateDoubleCountingAgreementsStatus, {
    invalidates: ["dc-agreement", "dc-agreements", "dc-snapshot"],
    onSuccess: () => {
      notify(t("Le statut a été changé avec succès."), { variant: "success" })
      onClose()
      onSuccess()
    },
    onError: (error) =>
      notifyError(
        error,
        t("Impossible de modifier le statut des agréments sélectionnés."),
        {
          AGREEMENTS_NOT_UPDATABLE: t(
            "Un ou plusieurs agréments ne sont plus actifs. Actualisez la liste puis réessayez."
          ),
        }
      ),
  })

  const handleConfirm = async () => {
    if (!selectedStatus || agreementIds.length === 0) return
    await updateStatuses.execute(entity.id, agreementIds, selectedStatus)
  }

  const loading = updateStatuses.loading
  const description = bulk
    ? t("Sélectionnez le nouveau statut pour les agréments sélectionnés.")
    : t("Sélectionnez le nouveau statut pour cet agrément.")

  return (
    <Dialog
      onClose={onClose}
      header={
        <>
          <Dialog.Title>{t("Changer le statut")}</Dialog.Title>
          <Dialog.Description>{description}</Dialog.Description>
        </>
      }
      footer={
        <>
          <Button priority="secondary" onClick={onClose} disabled={loading}>
            {t("Annuler")}
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!selectedStatus || loading}
            loading={loading}
          >
            {t("Confirmer")}
          </Button>
        </>
      }
    >
      <RadioGroup
        label={t("Statut")}
        options={availableStatuses.map((status) => ({
          label: getAgreementRegistrationStatusLabel(status, t),
          value: status,
        }))}
        value={selectedStatus}
        onChange={setSelectedStatus}
      />
    </Dialog>
  )
}

export { AgreementDetailsDialogChangeStatus }
