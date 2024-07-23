import { useTranslation } from "react-i18next"
import { Lot, LotError } from "transactions/types"
import Collapse from "common/components/collapse"
import { AlertOctagon, AlertTriangle } from "common/components/icons"
import Checkbox, { CheckboxGroup } from "common/components/checkbox"
import i18next from "i18next"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common/hooks/async"
import * as api from "../../api"
import { Normalizer } from "common/utils/normalize"
import { Fragment, useCallback, useEffect, useState } from "react"
import { UserRole } from "carbure/types"

export interface BlockingAnomaliesProps {
	anomalies: LotError[]
}

export const BlockingAnomalies = ({ anomalies }: BlockingAnomaliesProps) => {
	const { t } = useTranslation()
	return (
		<Collapse
			variant="danger"
			icon={AlertOctagon}
			isOpen={true}
			label={`${t("Erreurs")} (${anomalies.length})`}
		>
			<section>
				{t(
					"Vous ne pouvez pas valider ce lot tant que les problèmes suivants n'ont pas été adressés :"
				)}
			</section>

			<footer>
				<ul>
					{anomalies.map((anomaly, i) => (
						<li key={i}>{getAnomalyText(anomaly)}</li>
					))}
				</ul>
			</footer>
		</Collapse>
	)
}

export interface WarningAnomaliesProps {
	lot: Lot
	anomalies: LotError[]
}

export const WarningAnomalies = ({ lot, anomalies }: WarningAnomaliesProps) => {
	const { t } = useTranslation()
	const entity = useEntity()

	const isAcked = useCallback(
		(anomaly: LotError) => {
			const isCreator = lot.added_by?.id === entity.id
			const isRecipient = lot.carbure_client?.id === entity.id
			if (isCreator) return anomaly.acked_by_creator
			else if (isRecipient) return anomaly.acked_by_recipient
			else return false
		},
		[entity.id, lot]
	)

	const [checked, setChecked] = useState<string[] | undefined>([])

	useEffect(() => {
		setChecked(anomalies.filter(isAcked).map((a) => a.error))
	}, [anomalies, isAcked])

	const ackWarning = useMutation(
		(errors: string[], checked: boolean) => api.toggleWarning(entity.id, lot.id, errors, checked), // prettier-ignore
		{ invalidates: [] }
	)

	const hasEditRights = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)
	const isAllChecked = anomalies.every((a) => checked?.includes(a.error))

	return (
		<Collapse
			variant="warning"
			icon={AlertTriangle}
			label={`${t("Remarques")} (${anomalies.length})`}
		>
			<section>
				{t(
					"Des incohérences potentielles ont été détectées, elles n'empêchent pas la validation du lot mais peuvent donner lieu à un contrôle."
				)}
			</section>

			{hasEditRights && (
				<section>
					{t(
						"Si vous souhaitez ignorer certaines de ces remarques, vous pouvez cocher la case correspondante. Lorsque toutes les cases sont cochées, le lot n'apparait plus comme incohérent sur CarbuRe."
					)}
				</section>
			)}

			<section style={{ paddingBottom: "var(--spacing-m)" }}>
				{!hasEditRights && (
					<ul>
						{anomalies.map((anomaly, i) => (
							<li key={i}>{getAnomalyText(anomaly)}</li>
						))}
					</ul>
				)}

				{hasEditRights && (
					<Fragment>
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
							onToggle={(error, checked) => ackWarning.execute([error], checked)} // prettier-ignore
							normalize={normalizeAnomaly}
						/>
					</Fragment>
				)}
			</section>
		</Collapse>
	)
}

export const normalizeAnomaly: Normalizer<LotError, string> = (anomaly) => ({
	value: anomaly.error,
	label: getAnomalyText(anomaly),
})

export function getAnomalyText(anomaly: LotError) {
	const error = i18next.t(anomaly.error, { ns: "errors" }) || i18next.t("Erreur de validation") // prettier-ignore
	const extra = anomaly.extra && anomaly.extra !==  i18next.t(anomaly.error, { ns: "errors" }) ? ` - ${anomaly.extra}` : '' // prettier-ignore
	return error + extra
}

export function separateAnomalies(anomalies: LotError[]) {
	return [
		anomalies.filter((anomaly) => anomaly.is_blocking),
		anomalies.filter((anomaly) => !anomaly.is_blocking),
	]
}
