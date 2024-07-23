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
						key: "action",
						header: t("Action"),
						orderBy: (c) => c.action,
						cell: (c) => <Cell text={c.action} />,
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
	type: string
	action: string
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
			// flatten the updates so we have one row per change
			.flatMap((u) => {
				if (u.event_type === "UPDATED") {
					// retrocompatibility with old metadata model
					if ("field" in u.metadata) {
						return {
							type: "UPDATED",
							action: getEventTypeLabel(u.event_type),
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
								type: "UPDATED",
								action: getEventTypeLabel(u.event_type),
								field,
								user: u.user,
								date: u.event_dt,
								label: i18next.t(field.replace(/_id$/, ""), { ns: "fields" }),
								valueBefore: getFieldValue(valueBefore),
								valueAfter: getFieldValue(valueAfter),
							})
						)
					}
				} else {
					return {
						type: u.event_type,
						action: getEventTypeLabel(u.event_type),
						label: "",
						field: "",
						valueBefore: "",
						valueAfter: "",
						user: u.user,
						date: u.event_dt,
					}
				}

				return []
			})
			.filter((u) => {
				// always show non-update specific events
				if (u.type === "UPDATED") {
					// remove updates with fields that are not translated
					if (u.label === u.field) return false
					// remove updates that show no change
					if (u.valueBefore === u.valueAfter) return false
				} else {
					// only show actions that have a translation
					return u.action !== undefined
				}

				return true
			})
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

function getEventTypeLabel(type: string) {
	const matches: Record<string, string> = {
		CREATED: i18next.t("Création"),
		UPDATED: i18next.t("Modification"),
		UPDATED_BY_ADMIN: i18next.t("Modification par l'administration"),
		VALIDATED: i18next.t("Envoi"),
		// FIX_REQUESTED: i18next.t("Demande de correction"),
		// MARKED_AS_FIXED: i18next.t("Proposition de correction"),
		// FIX_ACCEPTED: i18next.t("Validation de correction"),
		ACCEPTED: i18next.t("Acceptation"),
		REJECTED: i18next.t("Refus"),
		// RECALLED: i18next.t("Demande de correction"),
		// DECLARED: i18next.t("Déclaration"),
		// DECLCANCEL: i18next.t("Annulation de déclaration"),
		DELETED: i18next.t("Suppression"),
		DELETED_BY_ADMIN: i18next.t("Suppression par l'administration"),
		// RESTORED: i18next.t(""),
		// CANCELLED: i18next.t("Renvoi en boite de réception"),
	}

	return matches[type]
}
