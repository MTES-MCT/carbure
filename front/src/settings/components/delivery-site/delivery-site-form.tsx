import { useTranslation } from "react-i18next"
import { findCountries } from "carbure/api"
import useEntity from "carbure/hooks/entity"
import {
  Depot,
  DepotType,
  Entity,
  EntityDepot,
  EntityType,
  OwnershipType,
} from "carbure/types"
import { normalizeCountry } from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Checkbox from "common/components/checkbox"
import Form, { useForm } from "common/components/form"
import { NumberInput, TextInput } from "common/components/input"
import { RadioGroup } from "common/components/radio"
import { Row } from "common/components/scaffold"
import { depotTypeOptions, ownerShipTypeOptions } from "./delivery-site.const"
import { AutoCompleteOperators } from "carbure/components/autocomplete-operators"
import { AutoCompleteCountries } from "carbure/components/autocomplete-countries"
import { useRef } from "react"

type DeliverySiteFormProps = {
  deliverySite?: EntityDepot
  onSubmit?: (values: DeliverySiteFormType) => void
  isReadOnly?: boolean

  // Submit button is outside the generic component, we have to pass the same id between form and button
  formId?: string
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
  > &
    Pick<EntityDepot, "ownership_type">
> & {
  blending_entity?: Entity | undefined
  blending_outsourced: boolean
}

const mapDeliverySiteToForm: (
  deliverySite?: EntityDepot
) => DeliverySiteFormType = (deliverySite) => ({
  name: deliverySite?.depot?.name ?? "",
  city: deliverySite?.depot?.city ?? "",
  country: deliverySite?.depot?.country,
  depot_id: deliverySite?.depot?.depot_id ?? "",
  depot_type: deliverySite?.depot?.depot_type ?? DepotType.Other,
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
  isReadOnly = false,
  onSubmit,
  formId = "delivery-site",
}: DeliverySiteFormProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind, setFieldError } = useForm<DeliverySiteFormType>(
    mapDeliverySiteToForm(deliverySite)
  )

  const depotIdRef = useRef<HTMLInputElement>(null)
  const checkDepotIdValidity = () => {
    const validityState = depotIdRef.current?.validity
    depotIdRef.current?.setCustomValidity("")

    if (validityState?.patternMismatch) {
      const message = t(
        "Cet identifiant douanier est invalide. Il doit être constitué de 15 caractères numériques."
      )
      depotIdRef.current?.setCustomValidity(message)
      depotIdRef.current?.reportValidity()
    }
  }

  return (
    <Form id={formId} onSubmit={() => onSubmit?.(value)}>
      <TextInput
        variant="outline"
        type="text"
        label={t("Nom du site")}
        {...bind("name")}
        readOnly={isReadOnly}
        required
      />

      <TextInput
        variant="outline"
        type="text"
        label={t("Identifiant officiel")}
        placeholder="Ex: FR1A00000580012"
        {...bind("depot_id")}
        readOnly={isReadOnly}
        required
        inputRef={depotIdRef}
        pattern="[0-9]{15}"
        onChange={(value) => {
          checkDepotIdValidity()
          bind("depot_id").onChange(value)
        }}
      />

      <RadioGroup
        label={t("Type de dépôt")}
        options={depotTypeOptions}
        {...bind("depot_type")}
        disabled={isReadOnly}
        required
      />

      <RadioGroup
        label={t("Propriété")}
        {...bind("ownership_type")}
        options={ownerShipTypeOptions}
        disabled={isReadOnly}
        required
      />

      {entity.entity_type === EntityType.Operator && (
        <>
          <Checkbox
            label={t("L'incorporation est effectuée par un tiers")}
            {...bind("blending_outsourced")}
            disabled={isReadOnly}
          />

          {value.blending_outsourced && (
            <AutoCompleteOperators
              label={t("Incorporateur Tiers")}
              readOnly={isReadOnly}
              required
              {...bind("blending_entity")}
            />
          )}
        </>
      )}
      {value.depot_type === DepotType.PowerPlant && (
        <NumberInput
          readOnly={isReadOnly}
          label={t("Rendement électrique")}
          min={0}
          max={1}
          step={0.1}
          {...bind("electrical_efficiency")}
          value={value.electrical_efficiency ?? undefined}
          required
        />
      )}
      {value.depot_type === DepotType.HeatPlant && (
        <NumberInput
          readOnly={isReadOnly}
          label={t("Rendement thermique")}
          min={0}
          max={1}
          step={0.1}
          {...bind("thermal_efficiency")}
          value={value.thermal_efficiency ?? undefined}
          required
        />
      )}
      {value.depot_type === DepotType.CogenerationPlant && (
        <NumberInput
          readOnly={isReadOnly}
          label={t("Température utile")}
          min={0}
          max={1}
          step={0.1}
          {...bind("useful_temperature")}
          value={value.useful_temperature ?? undefined}
          required
        />
      )}

      <TextInput
        readOnly={isReadOnly}
        label={t("Adresse")}
        {...bind("address")}
        required
      />

      <Row style={{ gap: "var(--spacing-s)" }}>
        <TextInput
          readOnly={isReadOnly}
          label={t("Ville")}
          {...bind("city")}
          required
        />
        <TextInput
          readOnly={isReadOnly}
          label={t("Code postal")}
          {...bind("postal_code")}
          required
        />
      </Row>

      {!isReadOnly ? (
        <AutoCompleteCountries
          label={t("Pays")}
          {...bind("country")}
          required
        />
      ) : (
        <TextInput
          readOnly
          label={t("Pays")}
          placeholder={t("Rechercher un pays...")}
          name="country"
          value={
            value.country
              ? (t(value.country.code_pays, { ns: "countries" }) as string)
              : ""
          }
        />
      )}
    </Form>
  )
}
