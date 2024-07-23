import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Return, Wrench } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useStatus } from "transactions/components/status"
import { TextInput } from "common/components/input"
import { LotSummary } from "../components/lots/lot-summary"
import { useMatomo } from "matomo"
import Form from "common/components/form"

export interface RequestManyFixesButtonProps {
	disabled?: boolean
	selection: number[]
}

export const RequestManyFixesButton = ({
	disabled,
	selection,
}: RequestManyFixesButtonProps) => {
	const { t } = useTranslation()
	const portal = usePortal()

	return (
		<Button
			disabled={disabled || selection.length === 0}
			variant="warning"
			icon={Wrench}
			label={t("Demander des corrections")}
			action={() =>
				portal((close) => (
					<RequestFixDialog summary selection={selection} onClose={close} />
				))
			}
		/>
	)
}

export interface RequestOneFixButtonProps {
	icon?: boolean
	lot: Lot
	hasParentStock?: boolean
}

export const RequestOneFixButton = ({
	icon,
	lot,
	hasParentStock,
}: RequestOneFixButtonProps) => {
	const { t } = useTranslation()
	const portal = usePortal()

	return (
		<Button
			captive
			variant={icon ? "icon" : "warning"}
			icon={Wrench}
			title={t("Demander une correction")}
			label={t("Demander une correction")}
			action={() =>
				portal((close) => (
					<RequestFixDialog
						selection={[lot.id]}
						onClose={close}
						hasParentStock={hasParentStock}
					/>
				))
			}
		/>
	)
}

interface RequestFixDialogProps {
	summary?: boolean
	selection: number[]
	onClose: () => void
	hasParentStock?: boolean
}

const RequestFixDialog = ({
	summary,
	selection,
	onClose,
	hasParentStock,
}: RequestFixDialogProps) => {
	const { t } = useTranslation()
	const notify = useNotify()
	const matomo = useMatomo()
	const status = useStatus()
	const entity = useEntity()
	const notifyError = useNotifyError()

	const v = variations(selection.length)

	const [comment = "", setComment] = useState<string | undefined>("")

	const requestFix = useMutation(requestFixAndCommentLots, {
		invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

		onSuccess: () => {
			const text = v({
				one: t("La correction a bien été demandée !"),
				many: t("Les corrections ont bien été demandées !"),
			})

			notify(text, { variant: "success" })
			onClose()
		},

		onError: (err) => {
			const text = v({
				one: t("La demande de correction a échoué !"),
				many: t("Les demandes de correction ont échoué !"),
			})

			notifyError(err, text)
			onClose()
		},
	})

	const query = useMemo(
		() => ({ status, entity_id: entity.id }),
		[status, entity.id]
	)

	return (
		<Dialog onClose={onClose}>
			<header>
				<h1>
					{v({
						one: t("Demander une correction"),
						many: t("Demander des corrections"),
					})}
				</h1>
			</header>
			<main>
				<section>
					{v({
						one: t("Voulez-vous demander une correction ?"),
						many: t("Voulez-vous demander des corrections pour les lots sélectionnés ?"), // prettier-ignore
					})}
					{hasParentStock && (
						<p>
							{t(
								"Attention la plupart des caractéristiques de durabilité de ce lot ont été définies dans un lot parent et ne pourront pas être modifiées directement sur ce lot enfant."
							)}
						</p>
					)}
				</section>
				<section>
					<Form id="request-fix">
						<TextInput
							autoFocus
							required
							label={t("Commentaire")}
							value={comment}
							onChange={setComment}
						/>
					</Form>
				</section>
				{summary && <LotSummary query={query} selection={selection} />}
			</main>
			<footer>
				<Button
					asideX
					submit="request-fix"
					loading={requestFix.loading}
					variant="warning"
					icon={Wrench}
					label={t("Demander correction")}
					action={() => {
						matomo.push([
							"trackEvent",
							"lot-corrections",
							"client-request-fix",
							"",
							selection.length,
						])
						requestFix.execute(entity.id, selection, comment)
					}}
				/>
				<Button
					disabled={requestFix.loading}
					icon={Return}
					label={t("Annuler")}
					action={onClose}
				/>
			</footer>
		</Dialog>
	)
}

async function requestFixAndCommentLots(
	entity_id: number,
	selection: number[],
	comment: string
) {
	await api.requestFix(entity_id, selection)
	await api.commentLots({ entity_id }, selection, comment)
}
