import { Form } from "common/components/form2"
import {
  CheckboxGroup,
  DateInput,
  NumberInput,
  RadioGroup,
  TextInput,
} from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { H2StationFormData, useStationForm } from "./station-form.hooks"
import { AccessType, DistributedPressure } from "h2/types"
import { ToggleSwitch } from "common/components/inputs2/toggle-switch/toggle-switch"
import { formatNumber } from "common/utils/formatters"

type StationFormProps = {
  onSubmit: (value?: H2StationFormData) => void
  children?: React.ReactNode
}

export const StationForm = ({ onSubmit, children }: StationFormProps) => {
  const { t } = useTranslation()

  const form = useStationForm()

  // PCI H2 = 120 MJ/kg
  const storageCapacityMJ = 120 * (form.value.storage_capacity ?? 0)

  return (
    <Form id="station-form" form={form} onSubmit={onSubmit}>
      <TextInput
        required
        label={t("Nom de la station (dans CarbuRe)")}
        {...form.bind("name")}
      />

      <TextInput
        required
        label={t("SIRET de la station")}
        {...form.bind("site_siret")}
      />

      <TextInput
        required
        label={t("Adresse de la station (Numéro et rue)")}
        {...form.bind("address")}
      />

      <Grid cols={2}>
        <TextInput required label={t("Ville")} {...form.bind("city")} />
        <TextInput
          required
          label={t("Code postal")}
          {...form.bind("postal_code")}
        />
      </Grid>

      <RadioGroup
        label={t("Nature du site")}
        options={[
          { value: AccessType.PUBLIC, label: t("Public") },
          { value: AccessType.PRIVATE, label: t("Privé") },
        ]}
        {...form.bind("access_type")}
      />

      <CheckboxGroup
        required
        label={t("Pression de l'hydrogène distribué")}
        options={[
          { value: DistributedPressure.Value350, label: t("350 bars") },
          { value: DistributedPressure.Value700, label: t("700 bars") },
        ]}
        {...form.bind("distributed_pressure")}
      />

      <ToggleSwitch
        label={t("Connecteurs compatibles avec les véhicules particuliers")}
        {...form.bind("has_personal_vehicle_connector")}
      />

      <NumberInput
        required
        label={t("Capacité de stockage sur site")}
        hintText={t("En kg")}
        min={1}
        {...form.bind("storage_capacity")}
        state="info"
        stateRelatedMessage={t("Soit {{energy}} MJ", {
          energy: formatNumber(storageCapacityMJ),
        })}
      />

      <NumberInput
        required
        label={t("Capacité de distribution")}
        hintText={t("En kg / jour")}
        min={1}
        {...form.bind("distribution_capacity")}
      />

      <DateInput
        required
        label={t("Date de mise en service")}
        {...form.bind("commissioning_date")}
      />
      {children}
    </Form>
  )
}
