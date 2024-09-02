import useEntity from "carbure/hooks/entity"
import { EntityPreview, EntityType } from "carbure/types"
import * as norm from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Return, Send } from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { formatPeriodFromDate } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafTicketSourceDetails } from "saf/types"
import * as api from "../../pages/operator/api"
import { PeriodSelect } from "./period-select"
import { VolumeInput } from "./volume-input"

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

  const { value, bind, setField, setFieldError } =
    useForm<AssignmentForm>(defaultAssignment)

  const remainingVolume =
    ticketSource.total_volume - ticketSource.assigned_volume

  const assignSafTicket = useMutation(api.assignSafTicket, {
    invalidates: [
      "ticket-source-details",
      "ticket-sources",
      "operator-snapshot",
    ],
  })

  const assignTicket = async () => {
    if (value.volume! < 1) {
      setFieldError("volume", t("Entrez un volume"))
      return
    }

    await assignSafTicket.execute(
      entity.id,
      ticketSource.id,
      value.volume!,
      value.assignment_period,
      value.client!,
      value.free_field!
    )
    onTicketAssigned(value.volume!, value.client!.name)
    onClose()
  }

  const setMaximumVolume = () => {
    setField("volume", remainingVolume)
  }

  const findSafClient = (query: string) => {
    return api.findClients(entity.id, query)
  }

  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
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
                "Veuillez remplir le formulaire ci-dessous afin d'affecter une partie ou tout le volume du lot à un client et générer un ticket de Carburant Durable d'Aviation"
              )}
            </p>

            <Form id="assign-ticket" onSubmit={assignTicket}>
              <VolumeInput
                remainingVolume={remainingVolume}
                onSetMaximumVolume={setMaximumVolume}
                {...bind("volume")}
              />
              <PeriodSelect
                deliveryPeriod={ticketSource.delivery_period}
                {...bind("assignment_period")}
              />

              <Autocomplete
                required
                label={t("Client")}
                getOptions={findSafClient}
                normalize={norm.normalizeEntityPreview}
                {...bind("client")}
              />

              {value.client?.entity_type === EntityType.Operator && (
                <TextInput //TODO for transfer only
                  required
                  label={t("N° du certificat d'acquisition")}
                  {...bind("agreement_reference")}
                />
              )}

              <TextInput label={t("Champ libre")} {...bind("free_field")} />
            </Form>
          </section>
        </main>

        <footer>
          <Button
            loading={assignSafTicket.loading}
            icon={Send}
            label={t("Affecter")}
            variant="primary"
            submit="assign-ticket"
          />

          <Button icon={Return} label={t("Retour")} action={onClose} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default TicketAssignment

const defaultAssignment = {
  volume: 0 as number | undefined,
  client: undefined as EntityPreview | undefined,
  assignment_period: formatPeriodFromDate(new Date()),
  agreement_reference: "" as string | undefined, //TODO for transfer only
  free_field: "" as string | undefined,
}

export type AssignmentForm = typeof defaultAssignment
