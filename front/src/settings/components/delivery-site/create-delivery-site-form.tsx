import { useTranslation } from "react-i18next"
import { Depot, DepotType, EntityDepot, OwnershipType } from "carbure/types"
import Form, { useForm } from "common/components/form"
import { NumberInput, TextInput } from "common/components/input"
import { RadioGroup } from "common/components/radio"
import { Row } from "common/components/scaffold"
import { depotTypeOptions } from "./delivery-site.const"
import { AutoCompleteCountries } from "carbure/components/autocomplete-countries"
import { useRef } from "react"

type DeliverySiteFormProps = {
  deliverySite?: EntityDepot
  onSubmit?: (values: DeliverySiteFormType) => void

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
  >
>

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
  onSubmit,
  formId = "delivery-site",
}: DeliverySiteFormProps) => {
  const { t } = useTranslation()
  const { value, bind } = useForm<DeliverySiteFormType>(
    mapDeliverySiteToForm(deliverySite)
  )

  const depotIdRef = useRef<HTMLInputElement>(null)
  const checkDepotIdValidity = () => {
    const validityState = depotIdRef.current?.validity
    depotIdRef.current?.setCustomValidity("")

    // if (validityState?.patternMismatch) {
    //   const message = t(
    //     "Cet identifiant douanier est invalide. Il doit être constitué de 15 caractères numériques."
    //   )
    //   depotIdRef.current?.setCustomValidity(message)
    //   depotIdRef.current?.reportValidity()
    // }
  }

  return (
    <Form id={formId} onSubmit={() => onSubmit?.(value)}>
      <TextInput
        variant="outline"
        type="text"
        label={t("Nom du site")}
        {...bind("name")}
        required
      />

      <TextInput
        variant="outline"
        type="text"
        label={t("Identifiant officiel")}
        placeholder="Ex: FR1A00000580012"
        {...bind("depot_id")}
        required
        inputRef={depotIdRef}
        // pattern="[0-9]{15}"
        onChange={(value) => {
          checkDepotIdValidity()
          bind("depot_id").onChange(value)
        }}
      />

      <RadioGroup
        label={t("Type de dépôt")}
        options={depotTypeOptions}
        {...bind("depot_type")}
        required
      />

      {value.depot_type === DepotType.PowerPlant && (
        <NumberInput
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
          label={t("Température utile")}
          min={0}
          max={1}
          step={0.1}
          {...bind("useful_temperature")}
          value={value.useful_temperature ?? undefined}
          required
        />
      )}

      <TextInput label={t("Adresse")} {...bind("address")} required />

      <Row style={{ gap: "var(--spacing-s)" }}>
        <TextInput label={t("Ville")} {...bind("city")} required />
        <TextInput label={t("Code postal")} {...bind("postal_code")} required />
      </Row>

      <AutoCompleteCountries label={t("Pays")} {...bind("country")} required />
    </Form>
  )
}
