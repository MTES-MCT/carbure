import useEntity from "common/hooks/entity"
import { EntityPreview, EntityType, Airport } from "common/types"
import * as norm from "common/utils/normalizers"
import Form, { useForm } from "common/components/form"
import { TextInput } from "common/components/inputs2"
import { formatPeriodFromDate } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import * as api from "saf/api"
import * as apiResources from "common/api"
import { PeriodSelect } from "./period-select"
import { VolumeInput } from "./volume-input"
import { ShippingMethodEnum } from "api-schema"
import { Autocomplete } from "common/components/autocomplete2"
import { ConsumptionType } from "saf/types"

export interface AssignmentFormProps {
  deliveryPeriod?: number
  remainingVolume: number
  onSubmit: (form: AssignmentFormData) => void
}

export const AssignmentForm = ({
  deliveryPeriod = defaultAssignment.assignment_period,
  remainingVolume,
  onSubmit,
}: AssignmentFormProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const { value, bind, setField } = useForm<AssignmentFormData>({
    ...defaultAssignment,
    assignment_period: deliveryPeriod,
  })

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
    <Form<AssignmentFormData>
      id="assign-ticket"
      onSubmit={() => onSubmit(value)}
    >
      <VolumeInput
        remainingVolume={remainingVolume}
        onSetMaximumVolume={setMaximumVolume}
        {...bind("volume")}
      />
      <PeriodSelect
        deliveryPeriod={deliveryPeriod}
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

      {clientIsAirline && (
        <TextInput
          label={t("Numéro de POS/POC")}
          placeholder="Ex: PC-ISCC-12345678"
          {...bind("pos_poc_number")}
        />
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
  )
}

const defaultAssignment = {
  volume: 0 as number | undefined,
  client: undefined as EntityPreview | undefined,
  assignment_period: formatPeriodFromDate(new Date()),
  agreement_reference: "" as string | undefined, //TODO for transfer only
  free_field: "" as string | undefined,
  reception_airport: undefined as Airport | undefined,
  shipping_method: undefined as ShippingMethodEnum | undefined,
  consumption_type: undefined as ConsumptionType | undefined,
  pos_poc_number: undefined as string | undefined,
}

export type AssignmentFormData = typeof defaultAssignment
