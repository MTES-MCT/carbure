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
      .flatMap((u) => {
        // backwards compatilibilty (maybe remove it later)
        if ("field" in u.metadata) {
          return {
            field: u.metadata.field,
            label: i18next.t(u.metadata.field, { ns: "fields" }),
            valueBefore: u.metadata.value_before,
            valueAfter: u.metadata.value_after,
            user: u.user,
            date: u.event_dt,
          }
        }

        return (u.metadata as LotFieldUpdate).changed.map(
          ([field, valueBefore, valueAfter]) => ({
            field,
            label: i18next.t(field, { ns: "fields" }),
            valueBefore,
            valueAfter,
            user: u.user,
            date: u.event_dt,
          })
        )
      })
      // remove updates with fields that are not translated
      .filter((u) => u.label !== u.field)
  )
}
