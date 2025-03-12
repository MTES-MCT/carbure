import { OperationText } from "accounting/components/operation-text"
import {
  RecipientToDepotForm,
  RecipientToDepotFormProps,
  RecipientToDepotSummary,
  showNextStepRecipientToDepotForm,
} from "accounting/components/recipient-to-depot-form"
import { findCountries } from "common/api"
import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { Step } from "common/components/stepper"
import { Country } from "common/types"
import { normalizeCountry } from "common/utils/normalizers"
import i18next from "i18next"
import { useTranslation } from "react-i18next"

export type CountryFormProps = RecipientToDepotFormProps & {
  country?: Country
}

/**
 * This component overrides the recipient-to-depot form to add a country field
 */
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
      />
      <RecipientToDepotForm />
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
    <RecipientToDepotSummary values={values}>
      <OperationText title={t("Pays")} description={values.country?.name} />
      <OperationText
        title={t("Etat membre")}
        description={values?.country?.is_in_europe ? t("Oui") : t("Non")}
      />
    </RecipientToDepotSummary>
  )
}

const showNextStepCountryForm = (values: CountryFormProps) => {
  return showNextStepRecipientToDepotForm(values) && Boolean(values.country)
}

export const countryFormStepKey = "country-form"
type CountryFormStepKey = typeof countryFormStepKey

export const countryFormStep: (
  values: RecipientToDepotFormProps
) => Step<CountryFormStepKey> = (values) => ({
  key: countryFormStepKey,
  title: i18next.t("Pays, client et dépôt destinataire"),
  allowNextStep: showNextStepCountryForm(values),
})
