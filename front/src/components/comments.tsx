import React, { useState } from "react"
import { Comment } from "../services/types"
import styles from "./comments.module.css"
import { AsyncButton, Box, Input } from "./system"
import { Collapsible } from "./system/alert"

type CommentsProps = {
  loading: boolean
  comments: Comment[]
  onComment: (c: string) => void
}

const Comments = ({ loading, comments, onComment }: CommentsProps) => {
  const [comment, setComment] = useState("")

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onComment(comment)
    setComment("")
  }

  return (
    <Collapsible
      level="warning"
      title={`Commentaires (${comments.length})`}
      className={styles.comments}
    >
      <table className={styles.commentsList}>
        <tbody>
          {comments.map((c, i) => (
            <tr key={i}>
              <td>
                <b>{c.entity.name}:</b>
              </td>
              <td>{c.comment}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <Box row as="form" className={styles.commentsForm} onSubmit={onSubmit}>
        <Input
          type="text"
          placeholder="Entrez un commentaire..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
        <AsyncButton submit loading={loading}>
          Envoyer
        </AsyncButton>
      </Box>
    </Collapsible>
  )
}

export default Comments
