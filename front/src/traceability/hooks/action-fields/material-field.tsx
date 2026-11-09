import i18next from "i18next"

import { findMaterials } from "common/api"
import { Autocomplete } from "common/components/autocomplete2"
import { normalizeActionMaterial } from "traceability/normalizers"
import { ActionMaterial } from "traceability/types"
import type { ActionField } from "./use-action-fields"

type InheritedMaterialKey = "previous_material" | "origin_material"

type MaterialFieldKey = "material" | InheritedMaterialKey

function materialFieldLabel(key: MaterialFieldKey) {
  if (key === "origin_material") return i18next.t("Matière d'origine")
  if (key === "previous_material") return i18next.t("Matière précédente")
  return i18next.t("Matière")
}

export function materialField(key: MaterialFieldKey = "material"): ActionField {
  return {
    key,
    label: materialFieldLabel(key),
    field: ({ form, props }) => {
      if (key === "material") {
        const bound = form.bind("material")

        return (
          <Autocomplete<ActionMaterial, ActionMaterial>
            {...props}
            {...bound}
            defaultOptions={bound.value ? [bound.value] : undefined}
            getOptions={findMaterials}
            normalize={normalizeActionMaterial}
          />
        )
      }

      const value = form.value.inherited_fields?.[key] ?? undefined

      return (
        <Autocomplete<ActionMaterial, ActionMaterial>
          {...props}
          readOnly
          value={value}
          defaultOptions={value ? [value] : undefined}
          normalize={normalizeActionMaterial}
        />
      )
    },
  }
}
