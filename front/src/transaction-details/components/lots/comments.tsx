import { useState } from "react"
import { useTranslation } from "react-i18next"
import { LotComment } from "../../types"
import { useMutation } from "common/hooks/async"
import { formatDateTime } from "common/utils/formatters"
import Collapse from "common/components/collapse"
import Form from "common/components/form"
import { TextInput } from "common/components/input"
import Button from "common/components/button"
import { Message } from "common/components/icons"
import * as api from "transactions/api"
import useEntity from "carbure/hooks/entity"
import { Lot } from "transactions/types"
export interface CommentsProps {
	readOnly?: boolean
	lot: Lot
	comments: LotComment[]
}

export const Comments = ({ readOnly, lot, comments }: CommentsProps) => {
	const { t } = useTranslation()
	const entity = useEntity()

	const [comment = "", setComment] = useState<string | undefined>()

	const addComment = useMutation(api.commentLots, {
		invalidates: ["lot-details"],
		onSuccess: () => setComment(""),
	})

	return (
		<Collapse
			icon={Message}
			variant="info"
			label={`${t("Commentaires")} (${comments.length})`}
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
				{!readOnly && (
					<Form
						variant="inline"
						onSubmit={() =>
							addComment.execute({ entity_id: entity.id }, [lot.id], comment)
						}
					>
						<TextInput
							clear
							value={comment}
							placeholder={t("Entrez un commentaire...")}
							onChange={setComment}
						/>
						<Button
							submit
							disabled={addComment.loading}
							variant="primary"
							label={t("Envoyer")}
						/>
					</Form>
				)}
			</footer>
		</Collapse>
	)
}

export default Comments
