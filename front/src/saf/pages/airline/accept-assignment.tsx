import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafTicket } from "saf/types"
import TicketTag from "../../components/tickets/tag"
import * as api from "./api"
import { EtsStatusEnum } from "api-schema"
import { RadioGroup } from "common/components/inputs2"

interface AcceptAssignmentProps {
  ticket: SafTicket
  onClose: () => void
}

type AcceptFormValue = {
  ets_status: EtsStatusEnum | undefined
}

const defaultAcceptFormValue: AcceptFormValue = {
  ets_status: undefined,
}

export const AcceptAssignment = ({
  ticket,
  onClose,
}: AcceptAssignmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const form = useForm<AcceptFormValue>(defaultAcceptFormValue)

  const acceptSafTicket = useMutation(api.acceptSafTicket, {
    invalidates: [
      "ticket-details",
      "airline-snapshot",
      "tickets",
      `nav-stats-${entity.id}`,
    ],
    onSuccess: () => ticketAccepted(),
  })

  const ticketAccepted = () => {
    notify(t("Le ticket a été accepté."), { variant: "success" })
    onClose()
  }

  const acceptTicket = async () => {
    await acceptSafTicket.execute(entity.id, ticket.id, form.value.ets_status!)
  }

  return (
    <Portal onClose={onClose}>
      <Dialog
        onClose={onClose}
        header={
          <Dialog.Title>
            <TicketTag status={ticket?.status} />
            {t("Ticket n°")}
            {ticket?.carbure_id ?? "..."}
          </Dialog.Title>
        }
        footer={
          <Button
            iconId="ri-check-line"
            customPriority="success"
            disabled={!form.value.ets_status}
            onClick={acceptTicket}
          >
            {t("Accepter le ticket")}
          </Button>
        }
      >
        <section>
          <Form id="accept-ticket" onSubmit={acceptTicket}>
            <p>
              {t(
                "Est-ce que ce ticket est concerné par une déclaration (ETS ou volontaire) ?"
              )}
            </p>

            <RadioGroup
              {...form.bind("ets_status")}
              required
              options={[
                {
                  value: EtsStatusEnum.ETS_VALUATION,
                  label: t("Valorisation ETS"),
                  hasTooltip: true,
                  title: t("RED SAF"),
                },
                {
                  value: EtsStatusEnum.NOT_CONCERNED,
                  label: t("Non concerné"),
                  hasTooltip: true,
                  title: t("ICAO CEF"),
                },
                {
                  value: EtsStatusEnum.OUTSIDE_ETS,
                  label: t("Volontaire"),
                  hasTooltip: true,
                  title: t("Hors obligation ETS"),
                },
              ]}
            />
          </Form>
        </section>
      </Dialog>
    </Portal>
  )
}

export default AcceptAssignment
