import { useTranslation } from "react-i18next"

import { Normalizer } from "common/utils/normalize"
import { EntityManager } from "common/hooks/entity"
import { ActionFilter, ActionStatus } from "traceability/types"
import { getActionStatusLabel } from "traceability/utils"

export type ActionFilterDisplay = {
  key: ActionFilter
  label: string
  normalizer?: Normalizer<string, string>
  condition?: (entity: EntityManager) => boolean
}

export function useActionFilters() {
  const { t } = useTranslation()

  return {
    holder: {
      key: ActionFilter.holder,
      label: t("Société"),
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
      normalizer: (status) => {
        return {
          value: status,
          label: getActionStatusLabel(status as ActionStatus),
        }
      },
    },

    type: {
      key: ActionFilter.type,
      label: t("Type"),
    },

    year: {
      key: ActionFilter.year,
      label: t("Année"),
    },

    period: {
      key: ActionFilter.period,
      label: t("Période"),
    },
  } satisfies Record<ActionFilter, ActionFilterDisplay>
}
