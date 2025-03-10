import useEntity from "common/hooks/entity"
import { EntityPreview, EntityType, Airport } from "common/types"
import * as norm from "common/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Button from "common/components/button"
import Collapse from "common/components/collapse"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Return, Send, Split } from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import {
  formatNumber,
  formatPeriod,
  formatPeriodFromDate,
} from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafTicketSource } from "saf/pages/operator/types"
import * as api from "../../pages/operator/api"
import * as apiResources from "common/api"
import { PeriodSelect } from "./period-select"
import { VolumeInput } from "./volume-input"
import Select from "common/components/select"
import { ConsumptionTypeEnum, ShippingMethodEnum } from "api-schema"

export interface TicketsGroupedAssignmentProps {
  ticketSources: SafTicketSource[]
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
                "Veuillez remplir le formulaire ci-dessous afin d'affecter une partie ou tout le volume des lots :"
              )}
            </p>

            <Collapse
              variant="info"
              icon={Split}
              label={t(
                "{{volumeCount}} volumes sélectionnés pour un total de {{remainingVolume}} L",
                {
                  volumeCount: ticketSources.length,
                  remainingVolume: formatNumber(remainingVolume),
                }
              )}
            >
              <section>
                <ul>
                  {ticketSources.map((ticketSource) => {
                    return (
                      <li key={ticketSource.id}>
                        {" "}
                        {t("{{volume}} L - {{period}} - {{feedstock}}", {
                          volume: formatNumber(
                            ticketSource.total_volume -
                              ticketSource.assigned_volume
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
              </section>
              <footer></footer>
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

                  <Select
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

                  <Select
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
                        label: t(
                          "Mise à consommation hors mandat (déclassement)"
                        ),
                      },
                    ]}
                  />
                </>
              )}

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

export default TicketsGroupedAssignment

const defaultAssignment = {
  volume: 0 as number | undefined,
  client: undefined as EntityPreview | undefined,
  assignment_period: formatPeriodFromDate(new Date()),
  free_field: "" as string | undefined,
  agreement_reference: "" as string | undefined, //TODO for transfer only
  reception_airport: undefined as Airport | undefined,
  shipping_method: undefined as ShippingMethodEnum | undefined,
  consumption_type: undefined as ConsumptionTypeEnum | undefined,
}

export type GroupedAssignmentForm = typeof defaultAssignment
