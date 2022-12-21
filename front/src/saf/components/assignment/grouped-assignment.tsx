import useEntity from "carbure/hooks/entity"
import { EntityPreview } from "carbure/types"
import * as norm from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Return, Send } from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafTicketSourceDetails } from "saf/types"
import * as api from "../../api"
import { PeriodSelect } from "./period-select"
import { VolumeInput } from "./volume-input"

export interface TicketAssignmentProps {
  ticketSources: SafTicketSourceDetails[]
  onClose: () => void
  onTicketsAssigned: (volume: number, clientName: string) => void
}
export const TicketAssignment = ({
  ticketSources,
  onClose,
  onTicketsAssigned,
}: TicketAssignmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const { value, bind, setField, setFieldError } =
    useForm<AssignmentForm>(defaultAssignment)

  const remainingVolume =
    ticketSources.reduce(
      (sum, ticketSource) => sum + ticketSource.total_volume,
      0
    ) -
    ticketSources.reduce(
      (sum, ticketSource) => sum + ticketSource.assigned_volume,
      0
    )

  const groupedAssignSafTicket = useMutation(api.groupedAssignSafTicket, {
    invalidates: ["ticket-sources", "operator-snapshot"],
  })

  const groupedAssignTicket = async () => {
    if (value.volume! < 1) {
      setFieldError("volume", t("Entrez un volume"))
      return
    }

    await groupedAssignSafTicket.execute(
      entity.id,
      ticketSources.map((ticketSource) => ticketSource.id),
      value.volume!,
      value.assignment_period,
      value.client!,
      value.free_field!
    )
    onTicketsAssigned(value.volume!, value.client!.name)
    onClose()
  }

  const setMaximumVolume = () => {
    setField("volume", remainingVolume)
  }

  const findSafClient = (query: string) => {
    return api.findClients(query)
  }

  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
        <header>
          <h1>{t("Affecter les volumes sélectionnés")}</h1>
        </header>

        <main>
          <section>
            <p>
              {t(
                "Veuillez remplir le formulaire ci-dessous afin d’affecter une partie ou tout le volume du lot à un client et générer un ticket de Carburant Durable d'Aviation"
              )}
            </p>

            <Form id="assign-ticket" onSubmit={groupedAssignTicket}>
              <VolumeInput
                remainingVolume={remainingVolume}
                onSetMaximumVolume={setMaximumVolume}
                {...bind("volume")}
              />
              <PeriodSelect
                deliveryPeriod={ticketSources[0].delivery_period} //TODO à partir de quel delivery period ?
                {...bind("assignment_period")}
              />

              <Autocomplete
                required
                label={t("Client")}
                getOptions={findSafClient}
                normalize={norm.normalizeEntityPreview}
                {...bind("client")}
              />

              <TextInput label={t("Champ libre")} {...bind("free_field")} />
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

          <Button icon={Return} label={t("Retour")} action={onClose} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default TicketAssignment

const formatPeriodFromDate = (date: Date) => {
  return date.getFullYear() * 100 + date.getMonth() + 1
}

const defaultAssignment = {
  volume: 0 as number | undefined,
  client: undefined as EntityPreview | undefined,
  assignment_period: formatPeriodFromDate(new Date()),
  free_field: "" as string | undefined,
}

export type AssignmentForm = typeof defaultAssignment
