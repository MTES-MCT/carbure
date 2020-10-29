import React, { useState } from "react"
import { Comment } from "../services/types"
import styles from "./comments.module.css"
import { Box, Button, Input } from "./system"

type CommentsProps = {
  comments: Comment[]
  onComment: (c: string) => void
}

const Comments = ({ comments, onComment }: CommentsProps) => {
  const [comment, setComment] = useState("")

  return (
    <Box as="fieldset" className={styles.comments}>
      <legend>Commentaires</legend>
      <ul>
        {comments.map((c, i) => (
          <li key={i}>
            {c.entity.name}: {c.comment}
          </li>
        ))}
      </ul>
      <Box row as="form" onSubmit={() => onComment(comment)}>
        <Input
          type="text"
          placeholder="Entrez un commentaire..."
          onChange={(e) => setComment(e.target.value)}
        />
        <Button submit level="primary">
          Envoyer
        </Button>
      </Box>
    </Box>
  )
}

export default Comments
