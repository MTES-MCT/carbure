import useEntity from "common/hooks/entity"
import { EntityPreview, EntityType, Airport } from "common/types"
import * as norm from "common/utils/normalizers"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import Form, { useForm } from "common/components/form"
import { TextInput } from "common/components/inputs2"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { formatPeriodFromDate } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafTicketSourceDetails } from "saf/pages/operator/types"
import * as api from "../../pages/operator/api"
import * as apiResources from "common/api"
import { PeriodSelect } from "./period-select"
import { VolumeInput } from "./volume-input"
import { ConsumptionTypeEnum, ShippingMethodEnum } from "api-schema"
import { Autocomplete } from "common/components/autocomplete2"

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

  const { value, bind, setField, setFieldError } = useForm<AssignmentForm>({
    ...defaultAssignment,
    assignment_period: ticketSource.delivery_period,
  })

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
      value.agreement_reference,
      value.free_field,
      value.reception_airport?.id,
      value.shipping_method,
      value.consumption_type
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

  const findAirports = (query: string) => {
    return apiResources.findAirports(query)
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

          {value.client?.entity_type === EntityType.Airline && (
            <>
              <Autocomplete
                required
                label={t("Aéroport de réception")}
                getOptions={findAirports}
                normalize={norm.normalizeAirport}
                {...bind("reception_airport")}
              />

              <Autocomplete
                label={t("Mode d'expédition")}
                placeholder={t("Choisissez un mode")}
                {...bind("shipping_method")}
                options={[
                  {
                    value: ShippingMethodEnum.PIPELINE,
                    label: t("Oléoduc"),
                  },
                  { value: ShippingMethodEnum.TRUCK, label: t("Camion") },
                  { value: ShippingMethodEnum.TRAIN, label: t("Train") },
                  { value: ShippingMethodEnum.BARGE, label: t("Barge") },
                ]}
              />

              <Autocomplete
                label={t("Type de consommation")}
                placeholder={t("Choisissez un type")}
                {...bind("consumption_type")}
                options={[
                  {
                    value: ConsumptionTypeEnum.MAC,
                    label: t("Mise à consommation mandat FR/EU"),
                  },
                  {
                    value: ConsumptionTypeEnum.MAC_DECLASSEMENT,
                    label: t("Mise à consommation hors mandat (déclassement)"),
                  },
                ]}
              />
            </>
          )}

          <TextInput label={t("Champ libre")} {...bind("free_field")} />
        </Form>
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
  reception_airport: undefined as Airport | undefined,
  shipping_method: undefined as ShippingMethodEnum | undefined,
  consumption_type: undefined as ConsumptionTypeEnum | undefined,
}

export type AssignmentForm = typeof defaultAssignment
