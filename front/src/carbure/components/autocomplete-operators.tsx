import { Entity } from "carbure/types"
import { normalizeEntity } from "carbure/utils/normalizers"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import { useTranslation } from "react-i18next"
import { findOperators } from "../api"

export const AutoCompleteOperators = (props: AutocompleteProps<Entity>) => {
  const { t } = useTranslation()

  return (
    <Autocomplete
      placeholder={t("Rechercher un opérateur pétrolier...")}
      getOptions={findOperators}
      normalize={normalizeEntity}
      {...props}
    />
  )
}
