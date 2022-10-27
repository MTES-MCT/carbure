import { findEntities } from "carbure/api"
import useEntity from "carbure/hooks/entity"
import { Entity, EntityPreview } from "carbure/types"
import * as norm from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Return, Send } from "common/components/icons"
import { DateInput, NumberInput, TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafTicketSourceDetails } from "saf/types"
import * as api from "../../api"

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

  const { value, errors, bind, setField, setFieldError } =
    useForm<AssignmentForm>(defaultAssignment)

  const remainingVolume =
    ticketSource.total_volume - ticketSource.assigned_volume

  const closeDialog = () => {
    onClose()
  }

  const assignSafTicket = useMutation(api.assignSafTicket, {
    invalidates: ["ticket-source-details", "ticket-sources"],
  })

  const assignTicket = async () => {
    if (value.volume! < 1) setFieldError("volume", t("Entrez un volume"))
    // TO TEST uncomment below
    await assignSafTicket.execute(
      entity.id,
      ticketSource.id,
      value.volume!,
      value.client!,
      value.agreement_reference,
      value.agreement_date
    )
    onTicketAssigned(value.volume!, value.client!.name)
    onClose()
  }

  const setMaximumVolume = () => {
    setField("volume", remainingVolume)
  }

  const findSafClient = (query: string) => {
    //TODO implement the query
    return api.findClients(query)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} fullscreen>
        <header>
          <h1>
            {t("Affecter le volume CAD n°")}
            {ticketSource?.carbure_id}
          </h1>
        </header>

        <main>
          <section>
            <p>
              {t(
                "Veuillez remplir le formulaire ci-dessous afin d’affecter une partie ou tout le volume du lot à un client et générer un ticket de Carburant Durable d'Aviation"
              )}
            </p>

            <Form id="assign-ticket" onSubmit={assignTicket}>
              <NumberInput
                required
                label={t("Volume ({{volume}} litres disponibles)", {
                  count: remainingVolume,
                  volume: formatNumber(remainingVolume),
                })}
                style={{ flex: 1 }}
                max={remainingVolume}
                min={0}
                type="number"
                {...bind("volume")}
                rightContent={
                  <Button
                    label={t("Maximum")}
                    action={setMaximumVolume}
                    variant="primary"
                  />
                }
              />

              <Autocomplete
                required
                label={t("Client")}
                getOptions={findSafClient}
                normalize={norm.normalizeEntityPreview}
                {...bind("client")}
              />

              <TextInput
                label={t("N° de Contrat (facture ou bon de commande)")}
                {...bind("agreement_reference")}
              />

              <DateInput
                label={t("Date du contrat (facture ou du bon de commande )")}
                {...bind("agreement_date")}
              />
            </Form>
          </section>
        </main>

        <footer>
          <Button
            icon={Send}
            label={t("Affecter")}
            variant="primary"
            submit="assign-ticket"
          />

          <Button icon={Return} label={t("Retour")} action={closeDialog} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default TicketAssignment

const defaultAssignment = {
  volume: 0 as number | undefined,
  client: undefined as EntityPreview | undefined,
  agreement_reference: undefined as string | undefined,
  agreement_date: undefined as string | undefined,
}

export type AssignmentForm = typeof defaultAssignment
