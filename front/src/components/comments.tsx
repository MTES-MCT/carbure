import React, { useState } from "react"
import { Comment } from "../services/types"
import styles from "./comments.module.css"
import { AsyncButton, Box, Input } from "./system"

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
    <Box as="fieldset" className={styles.comments}>
      <legend>Commentaires</legend>
      <ul>
        {comments.map((c, i) => (
          <li key={i}>
            <b>{c.entity.name}:</b> {c.comment}
          </li>
        ))}
      </ul>
      <Box row as="form" onSubmit={onSubmit}>
        <Input
          type="text"
          placeholder="Entrez un commentaire..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
        <AsyncButton submit loading={loading} level="primary">
          Envoyer
        </AsyncButton>
      </Box>
    </Box>
  )
}

export default Comments
