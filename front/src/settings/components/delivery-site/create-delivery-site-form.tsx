import { useTranslation } from "react-i18next"
import {
  Depot,
  DepotType,
  EntityDepot,
  EntityType,
  OwnershipType,
} from "carbure/types"
import Form, { useForm } from "common/components/form"
import { NumberInput, TextInput } from "common/components/input"
import { RadioGroup } from "common/components/radio"
import { Row } from "common/components/scaffold"
import { AutoCompleteCountries } from "carbure/components/autocomplete-countries"
import {
  useDeliverySiteFlags,
  useGetDepotTypeOptions,
} from "./delivery-site.hooks"
import useEntity from "carbure/hooks/entity"
import Checkbox from "common/components/checkbox"

type DeliverySiteFormProps = {
  deliverySite?: EntityDepot
  onCreate?: (values: DeliverySiteFormType) => void

  // Submit button is outside the generic component, we have to pass the same id between form and button
  formId?: string
  isReadOnly?: boolean
}

export type DeliverySiteFormType = Partial<
  Pick<
    Depot,
    | "name"
    | "city"
    | "country"
    | "depot_id"
    | "depot_type"
    | "address"
    | "postal_code"
    | "electrical_efficiency"
    | "thermal_efficiency"
    | "useful_temperature"
  >
>

const mapDeliverySiteToForm: (
  deliverySite?: EntityDepot
) => DeliverySiteFormType = (deliverySite) => ({
  name: deliverySite?.depot?.name ?? "",
  city: deliverySite?.depot?.city ?? "",
  country: deliverySite?.depot?.country,
  depot_id: deliverySite?.depot?.depot_id ?? "",
  depot_type: deliverySite?.depot?.depot_type ?? DepotType.OTHER,
  address: deliverySite?.depot?.address ?? "",
  postal_code: deliverySite?.depot?.postal_code ?? "",
  ownership_type: deliverySite?.ownership_type ?? OwnershipType.Own,
  blending_outsourced: deliverySite?.blending_is_outsourced ?? false,
  blending_entity: deliverySite?.blender ?? undefined,
  electrical_efficiency: deliverySite?.depot?.electrical_efficiency,
  thermal_efficiency: deliverySite?.depot?.thermal_efficiency,
  useful_temperature: deliverySite?.depot?.useful_temperature,
})

export const DeliverySiteForm = ({
  deliverySite,
  onCreate,
  formId = "delivery-site",
  isReadOnly = false,
}: DeliverySiteFormProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useForm<DeliverySiteFormType>(
    mapDeliverySiteToForm(deliverySite)
  )
  const { isCogenerationPlant, isHeatPlant, isPowerPlant } =
    useDeliverySiteFlags(value.depot_type)

  const depotTypeOptions = useGetDepotTypeOptions({ country: value.country })

  const handleSubmit = (values: DeliverySiteFormType) => {
    onCreate?.({
      name: values.name!,
      city: values.city!,
      country: values.country!,
      depot_id: values.depot_id!,
      depot_type: values.depot_type!,
      address: values.address!,
      postal_code: values.postal_code!,
      electrical_efficiency: isPowerPlant
        ? values.electrical_efficiency
        : undefined,
      thermal_efficiency: isHeatPlant ? values.thermal_efficiency : undefined,
      useful_temperature: isCogenerationPlant
        ? values.useful_temperature
        : undefined!,
    })
  }

  return (
    <Form id={formId} onSubmit={() => handleSubmit(value)}>
      <TextInput
        variant="outline"
        type="text"
        label={t("Nom du site")}
        {...bind("name")}
        required
        readOnly={isReadOnly}
      />

      <TextInput
        variant="outline"
        type="text"
        label={t("Identifiant officiel")}
        placeholder="Ex: FR1A00000580012"
        {...bind("depot_id")}
        required
        readOnly={isReadOnly}
      />

      <AutoCompleteCountries
        label={t("Pays")}
        {...bind("country")}
        required
        readOnly={isReadOnly}
      />

      <RadioGroup
        label={t("Type de dépôt")}
        options={depotTypeOptions}
        {...bind("depot_type")}
        required
        disabled={isReadOnly}
      />

      {(isCogenerationPlant || isPowerPlant) && (
        <NumberInput
          label={t("Rendement électrique (entre 0 et 1)")}
          step={1}
          {...bind("electrical_efficiency")}
          value={value.electrical_efficiency ?? undefined}
          required
          readOnly={isReadOnly}
        />
      )}
      {(isCogenerationPlant || isHeatPlant) && (
        <NumberInput
          label={t("Rendement thermique (entre 0 et 1)")}
          min={0}
          max={1}
          step={0.1}
          {...bind("thermal_efficiency")}
          value={value.thermal_efficiency ?? undefined}
          required
          readOnly={isReadOnly}
        />
      )}
      {isCogenerationPlant && (
        <NumberInput
          label={t("Température utile (°C)")}
          step={0.1}
          {...bind("useful_temperature")}
          value={value.useful_temperature ?? undefined}
          required
          readOnly={isReadOnly}
        />
      )}

      <TextInput
        label={t("Adresse")}
        {...bind("address")}
        required
        readOnly={isReadOnly}
      />

      <Row style={{ gap: "var(--spacing-s)" }}>
        <TextInput
          label={t("Ville")}
          {...bind("city")}
          required
          readOnly={isReadOnly}
          value={value.city ?? ""}
        />
        <TextInput
          label={t("Code postal")}
          {...bind("postal_code")}
          required
          readOnly={isReadOnly}
        />
      </Row>

      {entity.entity_type === EntityType.Operator &&
        deliverySite &&
        isReadOnly && (
          <>
            <Checkbox
              label={t("L'incorporation est effectuée par un tiers")}
              value={deliverySite.blending_is_outsourced}
              disabled
            />

            {deliverySite.blending_is_outsourced && (
              <TextInput
                label={t("Incorporateur Tiers")}
                value={deliverySite.blender?.name ?? ""}
                readOnly
              />
            )}
          </>
        )}
    </Form>
  )
}
