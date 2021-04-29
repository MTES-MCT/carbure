import React, { useState } from "react"
import { Comment, TransactionQuery } from "common/types"

import { Box, LoaderOverlay } from "common/components"
import { Input, LabelInput } from "common/components/input"
import { AsyncButton, Button } from "common/components/button"
import { Collapsible } from "common/components/alert"
import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import { Message } from "common/components/icons"
import RadioGroup from "common/components/radio-group"

import styles from "./form-comments.module.css"
import TransactionSummary, { useSummary } from "./summary"

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

type CommentPromptProps = PromptProps<string> & {
  title: string
  description: string
}

export const CommentPrompt = ({
  title,
  description,
  onResolve,
}: CommentPromptProps) => {
  const [comment, setComment] = useState("")

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onResolve(comment)
  }

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

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
            onClick={() => onResolve(comment)}
          >
            Confirmer
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </Box>
    </Dialog>
  )
}

export interface CommentWithType {
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
  onResolve,
}: PromptProps<CommentWithType>) => {
  const [comment, setComment] = useState("")
  const [topic, setTopic] = useState("")

  function onChangeTopic(e: React.ChangeEvent<HTMLInputElement>) {
    setTopic(e.target.value)
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (comment && topic) {
      onResolve({ comment, topic })
    }
  }

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text="Accepter lot" />
      <DialogText text="Voulez vous accepter ce lot sous réserve ?" />

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
            onClick={() => onResolve({ comment, topic })}
          >
            Accepter et demander une correction
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </Box>
    </Dialog>
  )
}

type CommentWithSummaryPromptProps = PromptProps<[string, number[]]> & {
  stock?: boolean
  title: string
  description: string
  query: TransactionQuery
  selection?: number[]
}

export const CommentWithSummaryPrompt = ({
  stock,
  title,
  description,
  query,
  selection,
  onResolve,
}: CommentWithSummaryPromptProps) => {
  const [comment, setComment] = useState("")
  const summary = useSummary(query, selection, stock)

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onResolve([comment, summary.data?.tx_ids ?? []])
  }

  return (
    <Dialog wide onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

      <Box as="form" onSubmit={onSubmit}>
        <LabelInput
          label="Commentaire (obligatoire)"
          value={comment}
          className={styles.commentInput}
          onChange={(e) => setComment(e.target.value)}
        />

        <TransactionSummary
          in={summary.data?.in ?? null}
          out={summary.data?.out ?? null}
        />

        <DialogButtons>
          <Button
            level="primary"
            disabled={!comment}
            onClick={() => onResolve([comment, summary.data?.tx_ids ?? []])}
          >
            Confirmer
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </Box>

      {summary.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default Comments
