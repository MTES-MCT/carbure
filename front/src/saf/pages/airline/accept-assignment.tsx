import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Check, Return } from "common/components/icons"
import { DateInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafTicket } from "saf/types"
import TicketTag from "../../components/tickets/tag"
import * as api from "./api"
import { RadioGroup } from "common/components/radio"
import { EtsStatusEnum } from "api-schema"

interface AcceptAssignmentProps {
  ticket: SafTicket
  onClose: () => void
}

const defaultAcceptFormValue = {
  ets_status: undefined as EtsStatusEnum | undefined,
  ets_declaration_date: undefined as string | undefined,
}

export const AcceptAssignment = ({
  ticket,
  onClose,
}: AcceptAssignmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const form = useForm(defaultAcceptFormValue)

  const acceptSafTicket = useMutation(api.acceptSafTicket, {
    invalidates: ["ticket-details", "airline-snapshot", "tickets"],
    onSuccess: () => ticketAccepted(),
  })

  const ticketAccepted = () => {
    notify(t("Le ticket a été accepté."), { variant: "success" })
    onClose()
  }

  const acceptTicket = async () => {
    await acceptSafTicket.execute(
      entity.id,
      ticket.id,
      form.value.ets_status!,
      form.value.ets_declaration_date
    )
  }

  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
        <header>
          <TicketTag status={ticket.status} />
          <h1>
            {t("Accepter le ticket n°")}
            {ticket?.carbure_id ?? "..."}
          </h1>
        </header>

        <main>
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
                  },
                  {
                    value: EtsStatusEnum.OUTSIDE_ETS,
                    label: t("Hors ETS (schéma volontaire)"),
                  },
                  {
                    value: EtsStatusEnum.NOT_CONCERNED,
                    label: t("Non concerné"),
                  },
                ]}
              />

              {form.value.ets_status &&
                form.value.ets_status !== EtsStatusEnum.NOT_CONCERNED && (
                  <>
                    <p>{t("J'indique la date de la déclaration :")}</p>

                    <DateInput
                      required
                      label={t("Date de déclaration")}
                      {...form.bind("ets_declaration_date")}
                    />
                  </>
                )}
            </Form>
          </section>
        </main>

        <footer>
          <Button
            icon={Check}
            disabled={!form.value.ets_status}
            label={t("Accepter le ticket")}
            variant="success"
            submit="accept-ticket"
          />

          <Button icon={Return} label={t("Retour")} action={onClose} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default AcceptAssignment
