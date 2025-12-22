import { Dialog } from "common/components/dialog2"
import { PortalInstance } from "common/components/portal"
import { DoubleCountingApplicationDetails } from "double-counting/types"
import { useTranslation } from "react-i18next"
import { useState } from "react"
import { Button } from "common/components/button2"
import { DoubleCountingStatus as DCStatus } from "double-counting/types"
import { getStatusLabel } from "double-counting/components/application-status"
import { RadioButtons } from "@codegouvfr/react-dsfr/RadioButtons"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import * as api from "../../../api"

type ApplicationDetailsDialogChangeStatusProps = {
  application: DoubleCountingApplicationDetails
  onClose: PortalInstance["close"]
  onSuccess: () => void
}

const ApplicationDetailsDialogChangeStatus = ({
  application,
  onClose,
  onSuccess,
}: ApplicationDetailsDialogChangeStatusProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const [selectedStatus, setSelectedStatus] = useState<DCStatus | undefined>(
    application.status
  )

  const updateStatus = useMutation(api.updateDoubleCountingApplicationStatus, {
    invalidates: ["dc-application", "dc-applications", "dc-snapshot"],
    onSuccess: () => {
      notify(t("Le statut a été changé avec succès."), { variant: "success" })
      onClose()
      onSuccess()
    },
  })

  // Available statuses to change to
  const availableStatuses = [
    DCStatus.PENDING,
    DCStatus.INPROGRESS,
    DCStatus.WAITING_FOR_DECISION,
  ]

  const handleConfirm = async () => {
    if (!selectedStatus) return
    await updateStatus.execute(entity.id, application.id, selectedStatus)
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <>
          <Dialog.Title>{t("Changer le statut")}</Dialog.Title>
          <Dialog.Description>
            {t("Sélectionnez le nouveau statut pour cette demande d'agrément.")}
          </Dialog.Description>
        </>
      }
      footer={
        <>
          <Button
            priority="secondary"
            onClick={onClose}
            disabled={updateStatus.loading}
          >
            {t("Annuler")}
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!selectedStatus || selectedStatus === application.status}
            loading={updateStatus.loading}
          >
            {t("Confirmer")}
          </Button>
        </>
      }
    >
      <RadioButtons
        legend={t("Statut")}
        options={availableStatuses.map((status) => ({
          label: getStatusLabel(status as any, t),
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

export default ApplicationDetailsDialogChangeStatus
