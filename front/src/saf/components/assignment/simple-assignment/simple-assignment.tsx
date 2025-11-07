import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "saf/api"
import { SafTicketSourceDetails } from "saf/types"
import { AssignmentForm, AssignmentFormData } from "../assignment-form"

export interface TicketAssignmentProps {
  ticketSource: SafTicketSourceDetails
  onClose: () => void
  onTicketAssigned: (volume: number, clientName: string) => void
}
export const TicketAssignment = ({
  ticketSource,
  onClose,
  onTicketAssigned,
}: TicketAssignmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const remainingVolume =
    ticketSource.total_volume - ticketSource.assigned_volume

  const assignSafTicket = useMutation(api.assignSafTicket, {
    invalidates: [
      "ticket-source-details",
      "ticket-sources",
      "operator-snapshot",
    ],
  })

  const assignTicket = async (value: AssignmentFormData) => {
    await assignSafTicket.execute(
      entity.id,
      ticketSource.id,
      value.volume!,
      value.assignment_period,
      value.client!,
      value.agreement_reference,
      value.free_field,
      value.reception_airport?.id,
      value.shipping_method,
      value.consumption_type,
      value.pos_poc_number
    )

    onTicketAssigned(value.volume!, value.client!.name)
    onClose()
  }

  return (
    <Portal onClose={onClose}>
      <Dialog
        onClose={onClose}
        header={
          <Dialog.Title>
            {t("Affecter le volume CAD n°")}
            {ticketSource?.carbure_id}
          </Dialog.Title>
        }
        footer={
          <Button
            loading={assignSafTicket.loading}
            iconId="ri-send-plane-line"
            priority="primary"
            nativeButtonProps={{
              form: "assign-ticket",
            }}
            type="submit"
          >
            {t("Affecter")}
          </Button>
        }
      >
        <p>
          {t(
            "Veuillez remplir le formulaire ci-dessous afin d'affecter une partie ou tout le volume du lot à un client et générer un ticket de Carburant Durable d'Aviation"
          )}
        </p>

        <AssignmentForm
          deliveryPeriod={ticketSource.delivery_period}
          remainingVolume={remainingVolume}
          onSubmit={assignTicket}
        />
      </Dialog>
    </Portal>
  )
}

export default TicketAssignment
