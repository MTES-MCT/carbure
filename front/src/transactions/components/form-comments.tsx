import React, { useState } from "react"
import { Comment } from "common/types"

import { AsyncButton, Box, Button, Input, LabelInput } from "common/components"
import { Collapsible } from "common/components/alert"
import { DialogButtons, PromptFormProps } from "common/components/dialog"
import { Message } from "common/components/icons"
import RadioGroup from "common/components/radio-group"

import styles from "./form-comments.module.css"

type CommentsProps = {
  readOnly: boolean
  loading: boolean
  comments: Comment[]
  onComment: (c: string) => void
}

const Comments = ({
  readOnly,
  loading,
  comments,
  onComment,
}: CommentsProps) => {
  const [comment, setComment] = useState("")

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onComment(comment)
    setComment("")
  }

  return (
    <Collapsible
      level="info"
      icon={Message}
      title={`Commentaires (${comments.length})`}
      className={styles.comments}
    >
      <table>
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

      {!readOnly && (
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
      )}
    </Collapsible>
  )
}

export const CommentPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<string>) => {
  const [comment, setComment] = useState("")

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onConfirm(comment)
  }

  return (
    <Box as="form" onSubmit={onSubmit}>
      <LabelInput
        label="Commentaire (obligatoire)"
        value={comment}
        className={styles.commentInput}
        onChange={(e) => setComment(e.target.value)}
      />

      <DialogButtons>
        <Button
          level="primary"
          disabled={!comment}
          onClick={() => onConfirm(comment)}
        >
          OK
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </DialogButtons>
    </Box>
  )
}

interface CommentWithType {
  comment: string
  topic: string
}

// prettier-ignore
const TOPICS = [
  { value: "sustainability", label: "Il y a un problème relatif à la durabilité ou aux caractéristiques du lot (provenance, volume, gaz à effet de serre)" },
  { value: "tx", label: "Il y a un problème sur la transaction (numéro douanier, site de livraison, date)" },
  { value: "both", label: "Les deux" },
]

export const CommentWithTypePrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<CommentWithType>) => {
  const [comment, setComment] = useState("")
  const [topic, setTopic] = useState("")

  function onChangeTopic(e: React.ChangeEvent<HTMLInputElement>) {
    setTopic(e.target.value)
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (comment && topic) {
      onConfirm({ comment, topic })
    }
  }

  return (
    <Box as="form" onSubmit={onSubmit}>
      <RadioGroup value={topic} options={TOPICS} onChange={onChangeTopic} />

      <LabelInput
        label="Commentaire (obligatoire)"
        value={comment}
        className={styles.commentInput}
        onChange={(e) => setComment(e.target.value)}
      />

      <DialogButtons>
        <Button
          level="primary"
          disabled={!comment || !topic}
          onClick={() => onConfirm({ comment, topic })}
        >
          Accepter et demander une correction
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </DialogButtons>
    </Box>
  )
}

export default Comments
