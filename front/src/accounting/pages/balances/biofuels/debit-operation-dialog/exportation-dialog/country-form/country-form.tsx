import { OperationText } from "accounting/components/operation-text"
import { findCountries } from "common/api"
import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { Step } from "common/components/stepper"
import { Country } from "common/types"
import { normalizeCountry } from "common/utils/normalizers"
import i18next from "i18next"
import { useTranslation } from "react-i18next"

export type CountryFormProps = {
  country?: Country
  export_recipient?: string
}

export const CountryForm = () => {
  const { bind } = useFormContext<CountryFormProps>()
  const { t } = useTranslation()

  return (
    <>
      <Autocomplete
        label={t("Pays")}
        {...bind("country")}
        placeholder={t("Rechercher un pays...")}
        getOptions={findCountries}
        normalize={normalizeCountry}
        required
      />
      <TextInput
        label={t("Destinataire")}
        {...bind("export_recipient")}
        placeholder={t("Ex: Nom de la société")}
      />
    </>
  )
}

export const CountryFormSummary = ({
  values,
}: {
  values: CountryFormProps
}) => {
  const { t } = useTranslation()

  return (
    <>
      {values?.export_recipient && (
        <OperationText
          title={t("Destinataire")}
          description={values?.export_recipient}
        />
      )}
      <OperationText title={t("Pays")} description={values.country?.name} />
      <OperationText
        title={t("Etat membre (UE)")}
        description={values?.country?.is_in_europe ? t("Oui") : t("Non")}
      />
    </>
  )
}

export const countryFormStepKey = "country-form"
type CountryFormStepKey = typeof countryFormStepKey

export const countryFormStep: Step<CountryFormStepKey> = {
  key: countryFormStepKey,
  title: i18next.t("Pays et client"),
}
