import { findCountries } from "carbure/api"
import { Country } from "carbure/types"
import { normalizeCountry } from "carbure/utils/normalizers"
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
