import { useCallback, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import Checkbox, { CheckboxGroup } from "common/components/checkbox"
import Collapse from "common/components/collapse"
import { AlertTriangle } from "common/components/icons"
import { useMutation } from "common/hooks/async"
import { normalizeAnomaly } from "transaction-details/components/lots/anomalies"
import { Lot, LotError } from "transactions/types"
import pickApi from "../api"

export interface WarningAnomaliesProps {
	lot: Lot
	anomalies: LotError[]
}

export const WarningAnomalies = ({ lot, anomalies }: WarningAnomaliesProps) => {
	const { t } = useTranslation()

	const entity = useEntity()
	const api = pickApi(entity)

	const [checked, setChecked] = useState<string[] | undefined>([])

	const isAcked = useCallback(
		(anomaly: LotError) => {
			if (entity.isAdmin) return anomaly.acked_by_admin
			else if (entity.isAuditor) return anomaly.acked_by_auditor
		},
		[entity.isAdmin, entity.isAuditor]
	)

	useEffect(() => {
		setChecked(anomalies.filter(isAcked).map((a) => a.error))
	}, [anomalies, isAcked])

	const ackWarning = useMutation((errors: string[], checked: boolean) =>
		api.toggleWarning(entity.id, lot.id, errors, checked)
	)

	const isAllChecked = anomalies.every((a) => checked?.includes(a.error))

	return (
		<Collapse
			variant="warning"
			icon={AlertTriangle}
			label={`${t("Remarques")} (${anomalies.length})`}
		>
			<section>
				{t(
					"Si vous souhaitez ignorer certaines de ces remarques, vous pouvez cocher la case correspondante. Lorsque toutes les cases sont cochées, le lot n'apparait plus comme incohérent sur CarbuRe."
				)}
			</section>

			<section style={{ paddingBottom: "var(--spacing-m)" }}>
				<Checkbox
					value={isAllChecked}
					style={{
						fontStyle: "italic",
						marginLeft: "var(--spacing-s)",
					}}
					label={t("Ignorer toutes ces remarques")}
					onChange={(checked) => {
						const errors = anomalies.map((a) => a.error)
						ackWarning.execute(errors, checked)
						setChecked(isAllChecked ? [] : errors)
					}}
				/>
				<CheckboxGroup
					variant="opacity"
					value={checked}
					options={anomalies}
					onChange={setChecked}
					onToggle={(error, checked) => ackWarning.execute([error], checked)}
					normalize={normalizeAnomaly}
				/>
			</section>
		</Collapse>
	)
}
