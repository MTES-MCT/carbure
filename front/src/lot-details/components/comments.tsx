import { useState } from "react"
import { useTranslation } from "react-i18next"
import { LotComment } from "../types"
import { formatDateTime } from "common-v2/utils/formatters"
import Collapse from "common-v2/components/collapse"
import Form from "common-v2/components/form"
import { TextInput } from "common-v2/components/input"
import Button from "common-v2/components/button"
import { Message } from "common-v2/components/icons"

export interface CommentsProps {
  comments: LotComment[]
}

export const Comments = ({ comments }: CommentsProps) => {
  const { t } = useTranslation()
  const [comment, setComment] = useState<string | undefined>()

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
        <Form variant="inline">
          <TextInput
            value={comment}
            placeholder={t("Entrez un commentaire...")}
            onChange={setComment}
          />
          <Button submit variant="primary" label={t("Envoyer")} />
        </Form>
      </footer>
    </Collapse>
  )
}

export default Comments
