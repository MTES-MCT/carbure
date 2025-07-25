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
import * as api from "saf/api"
import * as apiResources from "common/api"
import { PeriodSelect } from "../period-select"
import { VolumeInput } from "../volume-input"
import { ShippingMethodEnum } from "api-schema"
import { Autocomplete } from "common/components/autocomplete2"
import { ConsumptionType, SafTicketSourceDetails } from "saf/types"

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

  const supplierIsOperator = entity.isOperator
  const clientIsOperator = value.client?.entity_type === EntityType.Operator
  const clientIsAirline = value.client?.entity_type === EntityType.Airline
  const clientIsSafTrader = value.client?.entity_type === EntityType.SAF_Trader

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
            placeholder={t("Sélectionnez un client")}
            getOptions={findSafClient}
            normalize={norm.normalizeEntityPreview}
            {...bind("client")}
          />

          {clientIsOperator && (
            <TextInput //TODO for transfer only
              required
              label={t("N° du certificat d'acquisition")}
              placeholder={t("Ex: 1234567890")}
              {...bind("agreement_reference")}
            />
          )}

          {(clientIsAirline || clientIsSafTrader) && (
            <>
              <Autocomplete
                required
                label={t("Aéroport de réception")}
                placeholder={t("Sélectionnez un aéroport")}
                getOptions={findAirports}
                normalize={norm.normalizeAirport}
                {...bind("reception_airport")}
              />

              <Autocomplete
                label={t("Mode d'expédition")}
                placeholder={t("Sélectionnez un mode")}
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
            </>
          )}

          {/* Si fournisseur == Opérateur & client == Trader ou Cie. aérienne → type de conso
          Si fournisseur == Opérateur & client == Opérateur → PAS de type de conso (DAE)
          Si fournisseur == Trader & client == Cie. aérienne → PAS de type de conso */}

          {supplierIsOperator && (clientIsAirline || clientIsSafTrader) && (
            <Autocomplete
              label={t("Type de consommation")}
              placeholder={t("Sélectionnez un type")}
              {...bind("consumption_type")}
              options={[
                {
                  value: ConsumptionType.MAC,
                  label: t("Mise à consommation mandat FR/EU"),
                },
                {
                  value: ConsumptionType.MAC_DECLASSEMENT,
                  label: t("Mise à consommation hors mandat (déclassement)"),
                },
              ]}
            />
          )}

          <TextInput
            label={t("Champ libre")}
            {...bind("free_field")}
            placeholder={t("Ex: commentaire")}
          />
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
  consumption_type: undefined as ConsumptionType | undefined,
}

export type AssignmentForm = typeof defaultAssignment
