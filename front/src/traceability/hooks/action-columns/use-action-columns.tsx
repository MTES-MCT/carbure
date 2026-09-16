import { useTranslation } from "react-i18next"

import { Cell, Column } from "common/components/table2"
import { EntityManager } from "common/hooks/entity"
import { formatDate } from "common/utils/formatters"
import { ActionStatusBadge } from "traceability/components/action-status-badge"
import { Action } from "traceability/types"
import {
  ACTION_EMISSIONS_UNIT,
  formatActionTotalEmissions,
} from "traceability/utils/formatters"
import { quantityColumn } from "./quantity-column"

export type ActionColumn = Column<Action> & {
  condition?: (entity: EntityManager) => boolean
}

export function useActionColumns() {
  const { t } = useTranslation()

  return {
    status: {
      key: "status",
      header: t("Statut"),
      cell: (action) => <ActionStatusBadge status={action.status} />,
    },
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
      cell: (action) => <Cell text={action.material?.name} />,
    },

    certificate: {
      key: "certificate",
      header: t("N° de certificat"),
      cell: (action) => (
        <Cell text={action.certificate?.certificate_id ?? ""} />
      ),
    },

    quantity: quantityColumn(),
    mass: quantityColumn("mass"),
    volume: quantityColumn("volume"),
    energy: quantityColumn("energy"),

    site: {
      key: "site",
      header: t("Site"),
      cell: (action) => <Cell text={action.site?.name} />,
    },

    pos_id: {
      key: "pos_id",
      header: t("N° de POS"),
      cell: (action) => <Cell text={action.pos_id} />,
    },

    period: {
      key: "working_date",
      header: t("Période"),
      cell: (action) => (
        <Cell text={formatDate(action.working_date, "MM/yyyy")} />
      ),
    },

    working_date: {
      key: "working_date",
      header: t("Date de création"),
      cell: (action) => <Cell text={formatDate(action.working_date)} />,
    },

    total_emissions: {
      key: "total_emissions",
      header: t("Emissions"),
      cell: (action) => (
        <Cell
          text={formatActionTotalEmissions(action.total_emissions)}
          sub={ACTION_EMISSIONS_UNIT}
        />
      ),
    },
  } satisfies Record<string, ActionColumn>
}
