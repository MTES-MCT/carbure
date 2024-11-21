import { type EntityPreview } from "carbure/types"
import { normalizeEntityPreview } from "carbure/utils/normalizers"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import { useTranslation } from "react-i18next"
import { findOperators } from "../api"

export const AutoCompleteOperators = (
  props: AutocompleteProps<EntityPreview>
) => {
  const { t } = useTranslation()

  return (
    <Autocomplete
      placeholder={t("Rechercher un opérateur pétrolier...")}
      getOptions={findOperators}
      normalize={normalizeEntityPreview}
      {...props}
    />
  )
}
