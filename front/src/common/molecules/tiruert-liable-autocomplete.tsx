import { useTranslation } from "react-i18next"

import { findEntities } from "common/api"
import {
  Autocomplete,
  AutocompleteProps,
} from "common/components/autocomplete2"
import useEntity from "common/hooks/entity"
import { EntityPreview } from "common/types"
import { normalizeEntityPreview } from "common/utils/normalizers"

export const TiruertLiableAutocomplete = (
  props: Omit<AutocompleteProps<EntityPreview>, "getOptions" | "normalize">
) => {
  const { t } = useTranslation()
  const entity = useEntity()

  return (
    <Autocomplete
      placeholder={t("Rechercher un redevable")}
      {...props}
      getOptions={(query) =>
        findEntities(query, {
          is_enabled: true,
          is_tiruert_liable: true,
        }).then((entities) =>
          entities.filter((candidate) => candidate.id !== entity.id)
        )
      }
      normalize={normalizeEntityPreview}
    />
  )
}
