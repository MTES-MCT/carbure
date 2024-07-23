import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import {
	AlertCircle,
	Check,
	Cross,
	Plus,
	Return,
	Send,
} from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import Tag from "common/components/tag"
import { useMutation } from "common/hooks/async"
import { ElecChargePointsApplicationCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { addChargePoints } from "elec/api-cpo"
import { ReplaceAlert } from "./replace-alert"

export type ValidDetailsDialogProps = {
	fileData: ElecChargePointsApplicationCheckInfo
	onClose: () => void
	file: File
}

export const ValidDetailsDialog = ({
	fileData,
	onClose,
	file,
}: ValidDetailsDialogProps) => {
	const { t } = useTranslation()
	const entity = useEntity()
	const notify = useNotify()
	const notifyError = useNotifyError()
	const portal = usePortal()

	const chargePointsApplication = useMutation(addChargePoints, {
		invalidates: ["charge-points-applications"],
		onSuccess() {
			onClose()
			notify(
				t("Les {{count}} points de recharge ont été ajoutés !", {
					count: fileData.charge_point_count,
				}),
				{ variant: "success" }
			)
		},
		onError(err) {
			notifyError(
				err,
				t(
					"Impossible d'envoyer la demande d'inscription de points de recharges"
				)
			)
		},
	})

	const submitChargePointsApplication = () => {
		const confirmApplication = () => {
			chargePointsApplication.execute(entity.id, file)
		}
		if (fileData.pending_application_already_exists) {
			portal((resolve) => (
				<ReplaceApplicationConfirmDialog
					onClose={resolve}
					onConfirm={confirmApplication}
				/>
			))
		} else {
			confirmApplication()
		}
	}

	return (
		<Dialog onClose={onClose}>
			<header>
				<Tag big variant="success">
					{t("Valide")}
				</Tag>
				<h1>{t("Inscription des points de recharge")}</h1>
			</header>

			<main>
				<section>
					<p style={{ textAlign: "left" }}>
						<Trans
							values={{
								fileName: fileData.file_name,
							}}
							defaults="Votre fichier <b>{{fileName}}</b> ne comporte aucune erreur."
						/>
					</p>
					<p>
						<Trans
							count={fileData.charge_point_count}
							defaults="Les <b>{{count}} points de recharge</b> peuvent être inscrits à votre espace CarbuRe."
						/>
					</p>
					<p>
						<Trans>
							Un échantillon de points de recharge vous sera transmis
							directement par e-mail de notre part dans le but de réaliser un
							audit.
						</Trans>
					</p>

					{fileData.pending_application_already_exists && <ReplaceAlert />}
				</section>
			</main>

			<footer>
				<Button
					icon={Send}
					loading={chargePointsApplication.loading}
					label={
						fileData.pending_application_already_exists
							? t("Remplacer la demande d'inscription")
							: t("Envoyer la demande d'inscription")
					}
					variant="primary"
					action={submitChargePointsApplication}
				/>

				<Button icon={Return} label={t("Fermer")} action={onClose} asideX />
			</footer>
		</Dialog>
	)
}

export default ValidDetailsDialog

const ReplaceApplicationConfirmDialog = ({
	onClose,
	onConfirm,
}: {
	onClose: () => void
	onConfirm: () => void
}) => {
	const { t } = useTranslation()

	const confirmApplication = () => {
		onConfirm()
		onClose()
	}

	return (
		<Dialog onClose={onClose}>
			<header>
				<h1>{t("Remplacer la demande d'inscription ?")}</h1>
			</header>

			<main>
				<section>
					<p style={{ textAlign: "left" }}>
						<Trans>
							Souhaitez-vous confirmer le remplacement de la précédente demande
							d'inscription par celle-ci ?
						</Trans>
					</p>
				</section>
			</main>

			<footer>
				<Button
					icon={Check}
					label={t("Confirmer le remplacement")}
					variant="warning"
					action={confirmApplication}
				/>

				<Button icon={Return} label={t("Fermer")} action={onClose} asideX />
			</footer>
		</Dialog>
	)
}
