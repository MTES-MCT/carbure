import i18next from "i18next"
import { useTranslation } from "react-i18next"
import Collapse from "common-v2/components/collapse"
import { Edit } from "common-v2/components/icons"
import { Row } from "common-v2/components/scaffold"
import Table, { Cell } from "common-v2/components/table"
import { formatDateTime } from "common-v2/utils/formatters"
import { LotFieldUpdate, LotUpdate } from "lot-details/types"

export interface HistoryProps {
  changes: LotChange[]
}

export const History = ({ changes }: HistoryProps) => {
  const { t } = useTranslation()

  return (
    <Collapse
      icon={Edit}
      label={t("Historique des modifications ({{amount}})", { amount: changes.length })} // prettier-ignore
    >
      <Table
        rows={changes}
        columns={[
          {
            header: t("Date"),
            cell: (c) => <Cell text={formatDateTime(c.date)} />,
          },
          {
            header: t("Champ modifié"),
            cell: (c) => <Cell text={c.label} />,
          },
          {
            header: t("Valeur"),
            cell: (c) => <FieldChange change={c} />,
          },
          {
            header: t("Modifié par"),
            cell: (c) => c.user,
          },
        ]}
      />
    </Collapse>
  )
}

const FieldChange = ({ change }: { change: LotChange }) => {
  const valueBefore = change.valueBefore ? JSON.stringify(change.valueBefore) : "" // prettier-ignore
  const valueAfter = change.valueAfter ? JSON.stringify(change.valueAfter) : ""

  return (
    <Row title={`${valueBefore ?? "∅"} → ${valueAfter ?? "∅"}`}>
      {change.valueAfter && (
        <span style={{ marginRight: 12 }}>{valueAfter}</span>
      )}
      <span style={{ fontWeight: "normal", textDecoration: "line-through" }}>
        {valueBefore}
      </span>
    </Row>
  )
}

export interface LotChange {
  user: string
  date: string
  field: string
  label: string
  valueBefore: any
  valueAfter: any
}

export function getLotChanges(updates: LotUpdate<any>[] = []): LotChange[] {
  return (
    updates
      // only show updates for the moment
      .filter((u) => u.event_type === "UPDATED")
      // flatten the updates so we have one row per change
      .flatMap((u) =>
        (u.metadata as LotFieldUpdate).changed.map(
          ([field, valueBefore, valueAfter]) => ({
            field,
            label: i18next.t(field, { ns: "fields" }),
            valueBefore,
            valueAfter,
            user: u.user,
            date: u.event_dt,
          })
        )
      )
      // remove updates with fields that are not translated
      .filter((u) => u.label !== u.field)
  )
}
