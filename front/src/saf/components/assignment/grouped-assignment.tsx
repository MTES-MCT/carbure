import useEntity from "common/hooks/entity"
import { EntityPreview, EntityType, Airport } from "common/types"
import * as norm from "common/utils/normalizers"
import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { Dialog } from "common/components/dialog2"
import Form, { useForm } from "common/components/form"
import { TextInput } from "common/components/inputs2"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import {
  formatNumber,
  formatPeriod,
  formatPeriodFromDate,
} from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import * as api from "saf/api"
import * as apiResources from "common/api"
import { PeriodSelect } from "./period-select"
import { VolumeInput } from "./volume-input"
import { ShippingMethodEnum } from "api-schema"
import { Autocomplete } from "common/components/autocomplete2"
import { ConsumptionType, SafTicketSourcePreview } from "saf/types"

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

  const { value, bind, setField, setFieldError } =
    useForm<GroupedAssignmentForm>({
      ...defaultAssignment,
      assignment_period:
        lastDeliveryPeriod ?? defaultAssignment.assignment_period,
    })

  const groupedAssignSafTicket = useMutation(api.groupedAssignSafTicket, {
    invalidates: ["ticket-sources", "operator-snapshot"],
  })

  const groupedAssignTicket = async () => {
    if (value.volume! < 1) return setFieldError("volume", t("Entrez un volume"))

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

        <Form id="assign-ticket" onSubmit={groupedAssignTicket}>
          <VolumeInput
            remainingVolume={remainingVolume}
            onSetMaximumVolume={setMaximumVolume}
            {...bind("volume")}
          />
          {lastDeliveryPeriod && (
            <PeriodSelect
              deliveryPeriod={lastDeliveryPeriod}
              {...bind("assignment_period")}
            />
          )}

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

export default TicketsGroupedAssignment

const defaultAssignment = {
  volume: 0 as number | undefined,
  client: undefined as EntityPreview | undefined,
  assignment_period: formatPeriodFromDate(new Date()),
  free_field: "" as string | undefined,
  agreement_reference: "" as string | undefined, //TODO for transfer only
  reception_airport: undefined as Airport | undefined,
  shipping_method: undefined as ShippingMethodEnum | undefined,
  consumption_type: undefined as ConsumptionType | undefined,
}

export type GroupedAssignmentForm = typeof defaultAssignment
