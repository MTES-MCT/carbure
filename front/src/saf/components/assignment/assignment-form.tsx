import useEntity from "common/hooks/entity"
import { EntityPreview, EntityType, Airport } from "common/types"
import * as norm from "common/utils/normalizers"
import Form, { useForm } from "common/components/form"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { formatPeriodFromDate } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import * as api from "saf/api"
import { PeriodSelect } from "./period-select"
import { VolumeInput } from "./volume-input"
import { Autocomplete } from "common/components/autocomplete2"
import { ConsumptionType, SafShippingMethod, SafTicketSource } from "saf/types"

export interface AssignmentFormProps {
  showPosNumber?: boolean
  showOriginDepot?: boolean
  deliveryPeriod?: number
  remainingVolume: number
  posNumber?: string
  originDepot?: SafTicketSource["origin_lot_site"]
  onSubmit: (form: AssignmentFormData) => void
}

export const AssignmentForm = ({
  showPosNumber = false,
  showOriginDepot = false,
  deliveryPeriod,
  remainingVolume,
  posNumber,
  originDepot,
  onSubmit,
}: AssignmentFormProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const { value, bind, setField, setFieldError } = useForm<AssignmentFormData>({
    ...defaultAssignment,
    pos_number: posNumber,
    assignment_period: deliveryPeriod ?? defaultAssignment.assignment_period,
  })

  const setMaximumVolume = () => {
    setField("volume", remainingVolume)
  }

  const findSafClient = (query: string) => {
    return api.findClients(entity.id, query)
  }

  const findAirports = (query: string) => {
    return api.findAirports(
      query,
      false,
      originDepot?.id,
      value.shipping_method,
      value.has_intermediary_depot
    )
  }

  const handleSubmit = () => {
    if (value.volume! < 1) {
      return setFieldError("volume", t("Entrez un volume"))
    } else {
      onSubmit(value)
    }
  }

  const supplierIsOperator = entity.isOperator
  const clientIsOperator = value.client?.entity_type === EntityType.Operator
  const clientIsAirline = value.client?.entity_type === EntityType.Airline
  const clientIsSafTrader = value.client?.entity_type === EntityType.SAF_Trader

  return (
    <Form<AssignmentFormData> id="assign-ticket" onSubmit={handleSubmit}>
      <VolumeInput
        remainingVolume={remainingVolume}
        onSetMaximumVolume={setMaximumVolume}
        {...bind("volume")}
      />
      {deliveryPeriod && (
        <PeriodSelect
          deliveryPeriod={deliveryPeriod}
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

      {showOriginDepot && originDepot && (
        <TextInput
          disabled
          label={t("Dépôt du lot d'origine")}
          value={originDepot.name}
        />
      )}

      {(clientIsAirline || clientIsSafTrader) && (
        <>
          <Autocomplete
            label={t("Mode d'expédition")}
            placeholder={t("Sélectionnez un mode")}
            hasTooltip
            title={t(
              "En choisissant un mode d'expédition, la liste des aéroports accessibles s'adaptera en fonction du dépôt d'origine."
            )}
            {...bind("shipping_method")}
            options={[
              { value: SafShippingMethod.TRUCK, label: t("Camion") },
              { value: SafShippingMethod.TRAIN, label: t("Train") },
              { value: SafShippingMethod.BARGE, label: t("Barge") },
              { value: SafShippingMethod.SHIP, label: t("Bateau") },
              {
                value: SafShippingMethod.PIPELINE_DMM,
                label: t("Oléoduc DMM"),
              },
              {
                value: SafShippingMethod.PIPELINE_LHP,
                label: t("Oléoduc LHP"),
              },
              {
                value: SafShippingMethod.PIPELINE_ODC,
                label: t("Oléoduc ODC"),
              },
              {
                value: SafShippingMethod.PIPELINE_SPMR,
                label: t("Oléoduc SPMR"),
              },
              {
                value: SafShippingMethod.PIPELINE_SPSE,
                label: t("Oléoduc SPSE"),
              },
            ]}
          />

          <RadioGroup
            label={t("Dépôt intermédiaire ?")}
            hasTooltip
            title={t(
              "Ce champ permet d'indiquer la présence d'un dépôt de stockage intermédiaire avant la livraison finale à l'aéroport."
            )}
            options={norm.getYesNoOptions()}
            {...bind("has_intermediary_depot")}
          />

          <Autocomplete
            required
            label={t("Aéroport de réception")}
            placeholder={t("Sélectionnez un aéroport")}
            getOptions={findAirports}
            normalize={norm.normalizeAirport}
            hasTooltip
            title={t(
              "Si vous ne retrouvez pas l'aéroport désiré dans la liste, merci de contacter la DGEC en indiquant le dépôt d'origine et le mode de livraison."
            )}
            {...bind("reception_airport")}
          />
        </>
      )}

      {showPosNumber && (
        <TextInput
          label={t("Numéro de POS (hors Carbure)")}
          placeholder="Ex: PC-ISCC-12345678"
          {...bind("pos_number")}
          disabled={Boolean(posNumber)}
          hasTooltip
          title={t(
            "Remplissez ce champ si vous souhaitez que votre client puisse connaître le numéro de POS du lot d'origine généré par d'autres plateformes que Carbure. Notez qu'il sera ensuite affiché sur tous les tickets issus de ce lot."
          )}
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
  shipping_method: undefined as SafShippingMethod | undefined,
  consumption_type: undefined as ConsumptionType | undefined,
  pos_number: undefined as string | undefined,
  has_intermediary_depot: false,
}

export type AssignmentFormData = typeof defaultAssignment
