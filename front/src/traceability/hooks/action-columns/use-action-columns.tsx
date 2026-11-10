import { useTranslation } from "react-i18next"

import { Cell, Column } from "common/components/table2"
import { EntityManager } from "common/hooks/entity"
import { formatDate, formatUnitOnly } from "common/utils/formatters"
import { ActionStatusBadge } from "traceability/components/action-status-badge"
import { Action } from "traceability/types"
import {
  ACTION_EMISSIONS_UNIT,
  formatActionDecimal,
} from "traceability/utils/formatters"

export type ActionColumn = Column<Action> & {
  condition?: (entity: EntityManager) => boolean
}

export function useActionColumns() {
  const { t } = useTranslation()

  const pos_id: ActionColumn = {
    key: "pos_id",
    header: t("N° de POS"),
    cell: (action) => <Cell text={action.pos_id} />,
  }

  return {
    status: {
      key: "status",
      header: t("Statut"),
      cell: (action) => <ActionStatusBadge status={action.status} />,
    },
    holder: {
      key: "holder",
      header: t("Société"),
      cell: (action) => (
        <Cell text={action.holder.name} sub={action.holder.entity_type} />
      ),
    },

    material: {
      key: "material",
      header: t("Matière"),
      cell: (action) => <Cell text={action.material?.name} />,
    },

    origin_material: {
      key: "origin_material",
      header: t("Matière"),
      cell: (action) => (
        <Cell text={action.inherited_fields?.origin_material?.name} />
      ),
    },

    previous_material: {
      key: "previous_material",
      header: t("Dernière matière déclarée"),
      cell: (action) => (
        <Cell text={action.inherited_fields?.previous_material?.name} />
      ),
    },

    certificate: {
      key: "certificate",
      header: t("N° de certificat"),
      cell: (action) => (
        <Cell text={action.certificate?.certificate_id ?? ""} />
      ),
    },

    quantity: {
      key: "quantity",
      header: t("Quantité"),
      cell: (action) => {
        const text = formatActionDecimal(action.quantity)
        const unit =
          action.material?.unit ??
          action.inherited_fields?.previous_material?.unit

        return (
          <Cell
            text={text || "-"}
            sub={text && unit ? formatUnitOnly(unit) : undefined}
          />
        )
      },
    },

    site: {
      key: "site",
      header: t("Site"),
      cell: (action) => <Cell text={action.site?.name} />,
    },

    pos_id,

    carbure_id: {
      ...pos_id,
      header: t("Identifiant Carbure"),
    },

    period: {
      key: "working_date",
      header: t("Période"),
      cell: (action) => (
        <Cell text={formatDate(action.working_date, "MM/yyyy")} />
      ),
    },

    total_emissions: {
      key: "total_emissions",
      header: t("Emissions"),
      cell: (action) => (
        <Cell
          text={formatActionDecimal(action.total_emissions?.total)}
          sub={ACTION_EMISSIONS_UNIT}
        />
      ),
    },
  } satisfies Record<string, ActionColumn>
}
