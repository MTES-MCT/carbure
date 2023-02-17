import i18next from "i18next"
import { useTranslation } from "react-i18next"
import Collapse from "common/components/collapse"
import { History } from "common/components/icons"
import { Row } from "common/components/scaffold"
import Table, { Cell } from "common/components/table"
import { formatDateTime } from "common/utils/formatters"
import { LotFieldUpdate, LotUpdate } from "transaction-details/types"

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
      .filter((e) => e.event_type === "UPDATED" || e.event_type === "UPDATED_BY_ADMIN")
      // flatten the updates so we have one row per change
      .flatMap((u) => {
        if ("field" in u.metadata) {
          return {
            field: u.metadata.field,
            label: i18next.t(u.metadata.field, { ns: "fields" }),
            valueBefore: u.metadata.value_before,
            valueAfter: u.metadata.value_after,
            user: u.user,
            date: u.event_dt,
          }
        } else if ("changed" in u.metadata) {
          return (u.metadata as LotFieldUpdate).changed.map(
            ([field, valueBefore, valueAfter]) => ({
              field,
              user: u.user,
              date: u.event_dt,
              label: i18next.t(field, { ns: "fields" }),
              valueBefore: getFieldValue(valueBefore),
              valueAfter: getFieldValue(valueAfter),
            })
          )
        } else {
          return []
        }
      })
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
