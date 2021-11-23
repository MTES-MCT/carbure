import i18next from "i18next"
import { useTranslation } from "react-i18next"
import Collapse from "common-v2/components/collapse"
import { Edit } from "common-v2/components/icons"
import { Row } from "common-v2/components/scaffold"
import Table, { Cell } from "common-v2/components/table"
import { formatDateTime } from "common-v2/utils/formatters"
import { LotFieldUpdate, LotUpdate } from "lot-details/types"

export interface HistoryProps {
  updates: LotUpdate[]
}

export const History = ({ updates }: HistoryProps) => {
  const { t } = useTranslation()

  return (
    <Collapse
      icon={Edit}
      label={t("Historique des modifications ({{amount}})", { amount: updates.length })} // prettier-ignore
    >
      <Table
        rows={updates}
        columns={[
          {
            header: t("Date"),
            cell: (u) => <Cell text={formatDateTime(u.event_dt)} />,
          },
          {
            header: t("Champ modifié"),
            cell: (u) => <Cell text={u.label} />,
          },
          {
            header: t("Valeur"),
            cell: (u) => <FieldUpdate update={u.metadata} />,
          },
          {
            header: t("Modifié par"),
            cell: (u) => u.user,
          },
        ]}
      />
    </Collapse>
  )
}

const FieldUpdate = ({ update }: { update: LotFieldUpdate }) => (
  <Row>
    {update.value_after && (
      <span style={{ marginRight: 12 }}>{update.value_after}</span>
    )}
    <span style={{ fontWeight: "normal", textDecoration: "line-through" }}>
      {update.value_before}
    </span>
  </Row>
)

export function getLotUpdates(updates: LotUpdate<any>[] = []): LotUpdate[] {
  // prettier-ignore
  return updates
    .filter((u) => u.event_type === "UPDATED") // only show updates for the moment
    .map((u) => ({ ...u, label: i18next.t(u.metadata.field, { ns: "fields" }) })) // translate the field names
    .filter((u) => u.label !== u.metadata.field) // remove updates with fields that are not translated
}
