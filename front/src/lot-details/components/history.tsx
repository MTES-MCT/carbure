import i18next from "i18next"
import { useTranslation } from "react-i18next"
import Collapse from "common-v2/components/collapse"
import { History } from "common-v2/components/icons"
import { Row } from "common-v2/components/scaffold"
import Table, { Cell } from "common-v2/components/table"
import { formatDateTime } from "common-v2/utils/formatters"
import { LotFieldUpdate, LotUpdate } from "lot-details/types"

export interface HistoryProps {
  changes: LotChange[]
}

export const LotHistory = ({ changes }: HistoryProps) => {
  const { t } = useTranslation()

  return (
    <Collapse
      icon={History}
      label={t("Historique des modifications ({{amount}})", { amount: changes.length })} // prettier-ignore
    >
      <Table
        order={{ column: "date", direction: "desc" }}
        rows={changes}
        columns={[
          {
            key: "date",
            header: t("Date"),
            orderBy: (c) => c.date,
            cell: (c) => <Cell text={formatDateTime(c.date)} />,
          },
          {
            key: "label",
            header: t("Champ modifié"),
            orderBy: (c) => c.label,
            cell: (c) => <Cell text={c.label} />,
          },
          {
            header: t("Valeur"),
            cell: (c) => <FieldChange change={c} />,
          },
          {
            key: "user",
            header: t("Modifié par"),
            orderBy: (c) => c.user,
            cell: (c) => c.user,
          },
        ]}
      />
    </Collapse>
  )
}

const FieldChange = ({ change }: { change: LotChange }) => {
  const valueBefore = getFieldValue(change.valueBefore)
  const valueAfter = getFieldValue(change.valueAfter)

  return (
    <Row
      title={`${valueBefore ?? "∅"} → ${valueAfter ?? "∅"}`}
      style={{ flexWrap: "wrap" }}
    >
      {valueAfter && <span style={{ marginRight: 12 }}>{valueAfter}</span>}
      {valueBefore && (
        <span
          style={{ color: "var(--gray-dark)", textDecoration: "line-through" }}
        >
          {valueBefore}
        </span>
      )}
    </Row>
  )
}

export interface LotChange {
  user: string
  date: string
  field: string
  label: string
  valueBefore: string
  valueAfter: string
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
            user: u.user,
            date: u.event_dt,
            label: i18next.t(field, { ns: "fields" }),
            valueBefore: getFieldValue(valueBefore),
            valueAfter: getFieldValue(valueAfter),
          })
        )
      )
      // remove updates with fields that are not translated
      .filter((u) => u.label !== u.field)
      // remove updates that show no change
      .filter((u) => u.valueBefore !== u.valueAfter)
  )
}

function getFieldValue(value: any) {
  if (value instanceof Object && "name" in value) {
    return `${value.name}`
  } else if (["string", "number", "boolean"].includes(typeof value)) {
    return `${value}`
  } else {
    return ""
  }
}
