import { useTranslation } from "react-i18next"
import {
  Depot,
  SiteType,
  EntityDepot,
  EntityType,
  OwnershipType,
  EntityPreview,
} from "carbure/types"
import Form, { useForm } from "common/components/form"
import { NumberInput, TextInput } from "common/components/input"
import { RadioGroup } from "common/components/radio"
import { Row } from "common/components/scaffold"
import { AutoCompleteCountries } from "carbure/components/autocomplete-countries"
import { AutoCompleteOperators } from "carbure/components/autocomplete-operators"
import {
  useDeliverySiteFlags,
  useGetDepotTypeOptions,
  useOwnerShipTypeOptions,
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
    | "customs_id"
    | "site_type"
    | "address"
    | "postal_code"
    | "electrical_efficiency"
    | "thermal_efficiency"
    | "useful_temperature"
  > &
    Pick<EntityDepot, "ownership_type" | "blending_is_outsourced">
> & {
  blender?: EntityPreview
}

const mapDeliverySiteToForm: (
  deliverySite?: EntityDepot
) => DeliverySiteFormType = (deliverySite) => ({
  name: deliverySite?.depot?.name ?? "",
  city: deliverySite?.depot?.city ?? "",
  country: deliverySite?.depot?.country,
  customs_id: deliverySite?.depot?.customs_id ?? "",
  site_type: deliverySite?.depot?.site_type ?? SiteType.OTHER,
  address: deliverySite?.depot?.address ?? "",
  postal_code: deliverySite?.depot?.postal_code ?? "",
  ownership_type: deliverySite?.ownership_type ?? OwnershipType.OWN,
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
    useDeliverySiteFlags(value.site_type)

  const depotTypeOptions = useGetDepotTypeOptions({ country: value.country })
  const ownerShipTypeOptions = useOwnerShipTypeOptions()

  const handleSubmit = (values: DeliverySiteFormType) => {
    onCreate?.({
      name: values.name!,
      city: values.city!,
      country: values.country!,
      customs_id: values.customs_id!,
      site_type: values.site_type!,
      address: values.address!,
      postal_code: values.postal_code!,
      electrical_efficiency: isPowerPlant
        ? values.electrical_efficiency
        : undefined,
      thermal_efficiency: isHeatPlant ? values.thermal_efficiency : undefined,
      useful_temperature: isCogenerationPlant
        ? values.useful_temperature
        : undefined!,
      blender: values.blender,
      blending_is_outsourced: values.blending_is_outsourced,
      ownership_type: values.ownership_type,
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
        {...bind("customs_id")}
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
        {...bind("site_type")}
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

      {entity.entity_type === EntityType.Operator && (
        <>
          {isReadOnly && deliverySite ? (
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
          ) : (
            <>
              <RadioGroup
                label={t("Propriété")}
                options={ownerShipTypeOptions}
                {...bind("ownership_type")}
              />

              {entity && entity.entity_type === EntityType.Operator && (
                <Checkbox
                  label={t("Incorporation potentiellement effectuée par un tiers")} // prettier-ignore
                  {...bind("blending_is_outsourced")}
                  value={value.blending_is_outsourced ?? false}
                />
              )}

              {value.blending_is_outsourced && (
                <AutoCompleteOperators
                  label={t("Incorporateur Tiers")}
                  placeholder={t("Rechercher un opérateur pétrolier...")}
                  {...bind("blender")}
                />
              )}
            </>
          )}
        </>
      )}
    </Form>
  )
}
