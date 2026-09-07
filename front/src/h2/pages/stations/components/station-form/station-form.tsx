import { Form } from "common/components/form2"
import {
  Checkbox,
  CheckboxGroup,
  DateInput,
  NumberInput,
  RadioGroup,
  TextInput,
} from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { H2StationFormData, useStationForm } from "./station-form.hooks"
import { AccessType, DistributedPressure, H2Station } from "h2/types"
import { ToggleSwitch } from "common/components/inputs2/toggle-switch/toggle-switch"
import { formatNumber } from "common/utils/formatters"
import { SiretPicker } from "common/molecules/siret-picker"
import { SearchCompanyPreview } from "companies/types"

type StationFormProps = {
  readOnly?: boolean
  station?: H2Station
  onSubmit: (value?: H2StationFormData) => void
}

export const StationForm = ({
  readOnly,
  station,
  onSubmit,
}: StationFormProps) => {
  const { t } = useTranslation()

  const form = useStationForm(station)

  // PCI H2 = 120 MJ/kg
  const storageCapacityMJ = 120 * (form.value.storage_capacity ?? 0)

  function setCompanyInfo(company?: SearchCompanyPreview) {
    if (company) {
      form.setField("name", company.name)
      form.setField("address", company.registered_address)
      form.setField("city", company.registered_city)
      form.setField("postal_code", company.registered_zipcode)
    }
  }

  return (
    <Form id="station-form" form={form} onSubmit={onSubmit}>
      <SiretPicker
        required
        readOnly={readOnly}
        label={t("SIRET de la station")}
        onSelect={setCompanyInfo}
        {...form.bind("site_siret")}
      />

      <TextInput
        required
        readOnly={readOnly}
        label={t("Nom de la station")}
        {...form.bind("name")}
      />

      <TextInput
        required
        readOnly={readOnly}
        label={t("Adresse de la station (Numéro et rue)")}
        {...form.bind("address")}
      />

      <Grid cols={2}>
        <TextInput
          required
          readOnly={readOnly}
          label={t("Ville")}
          {...form.bind("city")}
        />
        <TextInput
          required
          readOnly={readOnly}
          label={t("Code postal")}
          {...form.bind("postal_code")}
        />
      </Grid>

      <TextInput
        disabled
        readOnly={readOnly}
        label={t("Pays")}
        value={t("France")}
      />

      <RadioGroup
        readOnly={readOnly}
        label={t("Nature du site")}
        options={[
          { value: AccessType.PUBLIC, label: t("Public") },
          { value: AccessType.PRIVATE, label: t("Privé") },
        ]}
        {...form.bind("access_type")}
      />

      <CheckboxGroup
        required
        readOnly={readOnly}
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
        disabled={readOnly}
      />

      <NumberInput
        required
        readOnly={readOnly}
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
        readOnly={readOnly}
        label={t("Capacité de distribution")}
        hintText={t("En kg / jour")}
        min={1}
        {...form.bind("distribution_capacity")}
      />

      <DateInput
        required
        readOnly={readOnly}
        label={t("Date de mise en service")}
        {...form.bind("commissioning_date")}
      />

      <Checkbox
        readOnly={readOnly}
        {...form.bind("has_compliant_measuring_instruments")}
        label={
          <span>
            <Trans>
              En cochant cette case, je déclare sur l’honneur que les
              instruments de mesure de la masse d'H2 sont conformes au{" "}
              <a
                href="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000579193"
                target="_blank"
              >
                Décret no 2001-387
              </a>{" "}
              du 3 mai 2001 relatif au contrôle des instruments de mesure
            </Trans>
          </span>
        }
      />
    </Form>
  )
}
