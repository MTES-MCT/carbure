import { useTranslation } from "react-i18next"
import { LotComment } from "transaction-details/types"
import { useMutation } from "common/hooks/async"
import { formatDateTime } from "common/utils/formatters"
import Collapse from "common/components/collapse"
import Form, { useForm } from "common/components/form"
import { TextInput } from "common/components/input"
import Button from "common/components/button"
import { Edit } from "common/components/icons"
import pickApi from "controls/api"
import useEntity from "carbure/hooks/entity"
import { Lot } from "transactions/types"
import Checkbox from "common/components/checkbox"

export interface ControlCommentsProps {
	lot: Lot
	comments: LotComment[]
}

export const ControlComments = ({ lot, comments }: ControlCommentsProps) => {
	const { t } = useTranslation()
	const entity = useEntity()
	const { isAdmin, isAuditor } = entity

	const form = useForm({
		comment: undefined as string | undefined,
		notifyExternal: false,
	})

	const api = pickApi(entity)

	const addComment = useMutation(api.commentLots, {
		invalidates: ["control-details"],
		onSuccess: () => form.setField("comment", ""),
	})

	const { comment, notifyExternal } = form.value

	return (
		<Collapse
			icon={Edit}
			variant="warning"
			label={`${t("Notes de contrôle")} (${comments.length})`}
		>
			<section>
				{comments.map((comment, i) => (
					<div key={i}>
						<b>
							[{formatDateTime(comment.comment_dt)}] {comment.entity.name}:
						</b>{" "}
						{comment.comment}
					</div>
				))}
			</section>

			<footer>
				<Form
					style={{ flex: 1 }}
					onSubmit={() => {
						if (comment) {
							addComment.execute(
								{ entity_id: entity.id },
								[lot.id],
								comment,
								isAdmin || (isAuditor && notifyExternal),
								isAuditor || (isAdmin && notifyExternal)
							)
						}
					}}
				>
					<Checkbox
						{...form.bind("notifyExternal")}
						label={
							isAdmin
								? t("Partager ce commentaire avec les auditeurs")
								: t("Partager ce commentaire avec l'administration")
						}
					/>

					<TextInput
						clear
						placeholder={t("Entrez un commentaire...")}
						{...form.bind("comment")}
						icon={
							<Button
								submit
								loading={addComment.loading}
								disabled={!comment}
								variant="primary"
								label={t("Envoyer")}
							/>
						}
					/>
				</Form>
			</footer>
		</Collapse>
	)
}

export default ControlComments
