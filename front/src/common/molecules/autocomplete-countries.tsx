import { findCountries } from "common/api"
import { Country } from "common/types"
import { normalizeCountry } from "common/utils/normalizers"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import { useTranslation } from "react-i18next"

export const AutoCompleteCountries = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()

  return (
    <Autocomplete
      placeholder={t("Rechercher un pays...")}
      getOptions={findCountries}
      normalize={normalizeCountry}
      {...props}
    />
  )
}
