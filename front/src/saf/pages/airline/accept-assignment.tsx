import useEntity from "common/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Check, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafTicket } from "saf/types"
import TicketTag from "../../components/tickets/tag"
import * as api from "./api"
import { RadioGroup } from "common/components/radio"
import { EtsStatusEnum } from "api-schema"
import Tooltip from "@codegouvfr/react-dsfr/Tooltip"

interface AcceptAssignmentProps {
  ticket: SafTicket
  onClose: () => void
}

const defaultAcceptFormValue = {
  ets_status: undefined as EtsStatusEnum | undefined,
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
                    label: (
                      <>
                        {t("Valorisation ETS")}
                        <Tooltip kind="hover" title={t("RED SAF")} />
                      </>
                    ),
                  },
                  {
                    value: EtsStatusEnum.NOT_CONCERNED,
                    label: (
                      <>
                        {t("Non concerné")}
                        <Tooltip kind="hover" title={t("ICAO CEF")} />
                      </>
                    ),
                  },
                  {
                    value: EtsStatusEnum.OUTSIDE_ETS,
                    label: (
                      <>
                        {t("Volontaire")}
                        <Tooltip
                          kind="hover"
                          title={t("Hors obligation ETS")}
                        />
                      </>
                    ),
                  },
                ]}
              />
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
