import { EntityPreview } from "common/types"
import { normalizeEntityPreview } from "common/utils/normalizers"
import {
  Autocomplete,
  AutocompleteProps,
} from "common/components/autocomplete2"
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
