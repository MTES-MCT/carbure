import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { Dialog } from "common/components/dialog2"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { formatNumber, formatPeriod } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import * as api from "saf/api"
import { SafTicketSourcePreview } from "saf/types"
import { AssignmentForm, AssignmentFormData } from "./assignment-form"

export interface TicketsGroupedAssignmentProps {
  ticketSources: SafTicketSourcePreview[]
  remainingVolume: number
  onClose: () => void
  onTicketsAssigned: (
    volume: number,
    clientName: string,
    assigned_tickets_count: number
  ) => void
}
const TicketsGroupedAssignment = ({
  ticketSources,
  remainingVolume,
  onClose,
  onTicketsAssigned,
}: TicketsGroupedAssignmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const lastDeliveryPeriod = ticketSources.sort(
    (a, b) => b.delivery_period - a.delivery_period
  )[0]?.delivery_period

  const groupedAssignSafTicket = useMutation(api.groupedAssignSafTicket, {
    invalidates: ["ticket-sources", "operator-snapshot"],
  })

  const groupedAssignTicket = async (value: AssignmentFormData) => {
    const response = await groupedAssignSafTicket.execute(
      entity.id,
      ticketSources.map((ticketSource) => ticketSource.id),
      value.volume!,
      value.assignment_period,
      value.client!,
      value.agreement_reference || "",
      value.free_field,
      value.reception_airport?.id,
      value.shipping_method,
      value.consumption_type
    )

    if (response.data) {
      onTicketsAssigned(
        value.volume!,
        value.client!.name,
        response.data.assigned_tickets_count
      )
      onClose()
    }
  }

  return (
    <Portal onClose={onClose}>
      <Dialog
        onClose={onClose}
        header={
          <Dialog.Title>{t("Affecter les volumes sélectionnés")}</Dialog.Title>
        }
        footer={
          <Button
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
        fitContent
      >
        <p>
          {t(
            "Veuillez remplir le formulaire ci-dessous afin d'affecter une partie ou tout le volume des lots :"
          )}
        </p>

        <Collapse
          defaultExpanded
          label={t(
            "{{count}} volumes sélectionnés pour un total de {{remainingVolume}} L",
            {
              count: ticketSources.length,
              remainingVolume: formatNumber(remainingVolume),
            }
          )}
        >
          <ul>
            {ticketSources.map((ticketSource) => {
              return (
                <li key={ticketSource.id}>
                  {" "}
                  {t("{{volume}} L - {{period}} - {{feedstock}}", {
                    volume: formatNumber(
                      ticketSource.total_volume - ticketSource.assigned_volume
                    ),
                    period: formatPeriod(ticketSource.delivery_period),
                    feedstock: t(ticketSource.feedstock?.code ?? "", {
                      ns: "feedstocks",
                    }),
                  })}
                </li>
              )
            })}
          </ul>
        </Collapse>

        <AssignmentForm
          groupSize={ticketSources.length}
          deliveryPeriod={lastDeliveryPeriod}
          remainingVolume={remainingVolume}
          onSubmit={groupedAssignTicket}
        />
      </Dialog>
    </Portal>
  )
}

export default TicketsGroupedAssignment
