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
    id: {
      key: "id",
      header: t("Id"),
      cell: (action) => <Cell text={action.id} />,
    },

    holder: {
      key: "holder",
      header: t("Détenteur"),
      cell: (action) => <Cell text={action.holder} />,
    },

    industry: {
      key: "industry",
      header: t("Filière"),
      cell: (action) => <Cell text={action.industry} />,
    },

    material: {
      key: "material",
      header: t("Matière"),
      cell: (action) => <Cell text={action.material} />,
    },

    quantity: {
      key: "quantity",
      header: t("Quantité de matière"),
      cell: (action) => <Cell text={action.quantity} />,
    },

    site: {
      key: "site",
      header: t("Site"),
      cell: (action) => <Cell text={action.site} />,
    },
  } satisfies Record<string, ActionColumn>
}
