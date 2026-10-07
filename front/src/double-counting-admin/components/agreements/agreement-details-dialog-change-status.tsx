import { Dialog } from "common/components/dialog2"
import { PortalInstance } from "common/components/portal"
import { useTranslation } from "react-i18next"
import { useState } from "react"
import { Button } from "common/components/button2"
import { RadioButtons } from "@codegouvfr/react-dsfr/RadioButtons"
import { AgreementStatusBulkUpdateRequestStatus } from "api-schema"
import { AgreementRegistrationStatus } from "double-counting/types"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
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

const statusLabels: Record<AgreementRegistrationStatus, string> = {
  [AgreementRegistrationStatus.VALID]: "Valide",
  [AgreementRegistrationStatus.SUSPENDED]: "Suspendu",
  [AgreementRegistrationStatus.WITHDRAWN]: "Retiré",
  [AgreementRegistrationStatus.TERMINATED]: "Interrompu",
}

const bulkStatusByStatus: Partial<
  Record<AgreementRegistrationStatus, AgreementStatusBulkUpdateRequestStatus>
> = {
  [AgreementRegistrationStatus.SUSPENDED]:
    AgreementStatusBulkUpdateRequestStatus.SUSPENDED,
  [AgreementRegistrationStatus.WITHDRAWN]:
    AgreementStatusBulkUpdateRequestStatus.WITHDRAWN,
  [AgreementRegistrationStatus.TERMINATED]:
    AgreementStatusBulkUpdateRequestStatus.TERMINATED,
}

const AgreementDetailsDialogChangeStatus = ({
  agreementIds,
  bulk = false,
  initialStatus,
  onClose,
  onSuccess,
}: AgreementDetailsDialogChangeStatusProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
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
  })
  const updateStatuses = useMutation(api.updateDoubleCountingAgreementsStatus, {
    invalidates: ["dc-agreements", "dc-snapshot"],
    onSuccess: () => {
      notify(t("Le statut a été changé avec succès."), { variant: "success" })
      onClose()
      onSuccess()
    },
  })

  const handleConfirm = async () => {
    if (!selectedStatus || agreementIds.length === 0) return
    const agreementId = agreementIds[0]
    if (!bulk && agreementIds.length === 1 && agreementId !== undefined) {
      await updateStatus.execute(entity.id, agreementId, selectedStatus)
    } else {
      const bulkStatus = bulkStatusByStatus[selectedStatus]
      if (bulkStatus) {
        await updateStatuses.execute(entity.id, agreementIds, bulkStatus)
      }
    }
  }

  const loading = updateStatus.loading || updateStatuses.loading
  const statuses = bulk ? availableStatuses.slice(1) : availableStatuses
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
      <RadioButtons
        legend={t("Statut")}
        options={statuses.map((status) => ({
          label: t(statusLabels[status]),
          nativeInputProps: {
            value: status,
            checked: selectedStatus === status,
            onChange: () => setSelectedStatus(status),
          },
        }))}
      />
    </Dialog>
  )
}

export { AgreementDetailsDialogChangeStatus }
