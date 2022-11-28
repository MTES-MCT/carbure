import { findEntities } from "carbure/api"
import useEntity from "carbure/hooks/entity"
import { Entity, EntityPreview } from "carbure/types"
import * as norm from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Return, Send } from "common/components/icons"
import {
  DateInput,
  Field,
  Input,
  NumberInput,
  TextInput,
} from "common/components/input"
import Portal from "common/components/portal"
import { Row } from "common/components/scaffold"
import Select from "common/components/select"
import { useMutation } from "common/hooks/async"
import {
  capitalize,
  formatDate,
  formatNumber,
  formatPeriod,
} from "common/utils/formatters"
import { Option } from "common/utils/normalize"
import { useEffect, useState } from "react"
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

    // TO TEST uncomment below
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
    return api.findClients(query)
  }

  //TODO get years and months
  const years = [2022, 2023]
  const months = [1]

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
                step={0.01}
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

              <PeriodSelect
                //TODO
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

interface PeriodSelectProps {
  deliveryPeriod: number
  onChange: (value: number) => void
}

const PeriodSelect = ({ deliveryPeriod, onChange }: PeriodSelectProps) => {
  const { t } = useTranslation()
  const [periodList, setPeriodList] = useState<Option<number>[]>()
  const [period, _setPeriod] = useState<number>(deliveryPeriod)

  const setPeriod = (period: number) => {
    _setPeriod(period)
    onChange(period)
  }

  useEffect(() => {
    let month: number = deliveryPeriod % 100
    let year: number = Math.floor(deliveryPeriod / 100)
    const list: Option<number>[] = []
    for (let i = year; i <= year + 1; i++) {
      let j = i === year ? month : 1
      for (; j <= 12; j++) {
        const period = i * 100 + j
        const date = formatPeriod(period) + "-01"
        const periodString = formatDate(date, {
          day: undefined,
          year: "numeric",
          month: "long",
        })

        list.push({
          value: period,
          label: capitalize(periodString),
        })
      }
    }
    setPeriodList(list)
  }, [])

  return (
    <Select
      placeholder={t("Choisissez une année")}
      value={period}
      onChange={(period) => setPeriod(period!)}
      options={periodList}
    />
  )
}
