import { useTranslation } from "react-i18next"

import { Normalizer } from "common/utils/normalize"
import { EntityManager } from "common/hooks/entity"
import { ActionFilter } from "traceability/types"

export type ActionFilterDisplay = {
  key: ActionFilter
  label: string
  normalizer?: Normalizer<unknown, string>
  condition?: (entity: EntityManager) => boolean
}

export function useActionFilters() {
  const { t } = useTranslation()

  return {
    holder: {
      key: ActionFilter.holder,
      label: t("Détenteur"),
    },

    material: {
      key: ActionFilter.material,
      label: t("Matière"),
    },

    order_by: {
      key: ActionFilter.order_by,
      label: t("Tri"),
    },

    shipping_method: {
      key: ActionFilter.shipping_method,
      label: t("Mode de transport"),
    },

    site: {
      key: ActionFilter.site,
      label: t("Site"),
    },

    status: {
      key: ActionFilter.status,
      label: t("Statut"),
    },

    type: {
      key: ActionFilter.type,
      label: t("Type"),
    },

    year: {
      key: ActionFilter.year,
      label: t("Année"),
    },
  } satisfies Record<ActionFilter, ActionFilterDisplay>
}
