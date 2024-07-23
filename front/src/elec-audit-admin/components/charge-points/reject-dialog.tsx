import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "../../api"
import ApplicationStatus from "elec/components/application-status"
import {
	ElecChargePointsApplication,
	ElecAuditApplicationStatus,
} from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { useState } from "react"
import Checkbox from "common/components/checkbox"
export type ApplicationDialogProps = {
	application: ElecChargePointsApplication
	onClose: () => void
	onRejected: () => void
	forceRejection: boolean
}

export const ChargePointsApplicationRejectDialog = ({
	application,
	onClose,
	forceRejection,
	onRejected,
}: ApplicationDialogProps) => {
	const { t } = useTranslation()
	const entity = useEntity()
	const notify = useNotify()
	const notifyError = useNotifyError()
	const [confirmCheckbox, setConfirmCheckbox] = useState(false)

	const rejectChargePointsApplication = useMutation(
		api.rejectChargePointsApplication,
		{
			invalidates: [
				"audit-charge-points-applications",
				"elec-admin-audit-snapshot",
			],
			onSuccess() {
				onClose()
				onRejected()
				notify(
					t(
						"La demande d'inscription pour les {{count}} points de recharge a été refusée !",
						{ count: application.charge_point_count }
					),
					{ variant: "success" }
				)
			},
			onError(err) {
				notifyError(
					err,
					t("Impossible de refuser l'inscription des points de recharge")
				)
			},
		}
	)

	const rejectApplication = () => {
		rejectChargePointsApplication.execute(
			entity.id,
			application.id,
			forceRejection
		)
	}

	return (
		<Dialog onClose={onClose}>
			<header>
				<ApplicationStatus status={application.status} big />
				<h1>{t("Refuser les points de recharge")}</h1>
			</header>

			<main>
				<section>
					<p style={{ textAlign: "left" }}>
						<Trans
							values={{
								applicationDate: formatDate(application.application_date),
							}}
							count={application.charge_point_count}
							defaults="Refuser les <b>{{count}}</b> points de recharge importés le {{applicationDate}} ?"
						/>
					</p>
					<p>
						<Checkbox
							value={confirmCheckbox}
							onChange={setConfirmCheckbox}
							label={t(
								" Je confirme avoir partagé le motif de mon refus à l'aménageur par e-mail."
							)}
						/>
					</p>
				</section>
			</main>

			<footer>
				<Button
					icon={Check}
					label={
						forceRejection
							? t("Refuser la demande sans audit")
							: t("Refuser la demande")
					}
					variant="danger"
					action={rejectApplication}
					loading={rejectChargePointsApplication.loading}
					disabled={!confirmCheckbox}
				/>

				<Button icon={Return} label={t("Fermer")} action={onClose} asideX />
			</footer>
		</Dialog>
	)
}

export default ChargePointsApplicationRejectDialog
