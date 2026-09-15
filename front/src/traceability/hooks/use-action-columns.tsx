import { useTranslation } from "react-i18next"

import { Cell, Column } from "common/components/table2"
import { EntityManager } from "common/hooks/entity"
import { Action } from "traceability/types"

export type ActionColumn = Column<Action> & {
  condition?: (entity: EntityManager) => boolean
}

export function useActionColumns() {
  const { t } = useTranslation()

  return {
    holder: {
      key: "holder",
      header: t("Détenteur"),
      cell: (action) => (
        <Cell text={action.holder.name} sub={action.holder.entity_type} />
      ),
    },

    material: {
      key: "material",
      header: t("Matière"),
      cell: (action) => <Cell text={action.material.name} />,
    },

    quantity: {
      key: "quantity",
      header: t("Quantité"),
      cell: (action) => <Cell text={action.quantity} />,
    },

    site: {
      key: "site",
      header: t("Site"),
      cell: (action) => <Cell text={action.site.name} />,
    },
  } satisfies Record<string, ActionColumn>
}
