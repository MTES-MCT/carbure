import React from "react"

import { LotStatus } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotAcceptor } from "transactions/hooks/actions/use-accept-lots"
import { LotRejector } from "transactions/hooks/actions/use-reject-lots"
import { LotValidator } from "transactions/hooks/actions/use-validate-lots"
import { useRelativePush } from "common/components/relative-route"

import styles from "../components/form.module.css"

import useTransactionDetails from "../hooks/use-transaction-details"

import {
  AlertTriangle,
  Check,
  Cross,
  Return,
  Save,
  ChevronLeft,
  ChevronRight,
} from "common/components/icons"
import { Box, LoaderOverlay } from "common/components"
import { AsyncButton, Button } from "common/components/button"
import Modal from "common/components/modal"
import TransactionForm from "../components/form"
import { StatusTitle } from "../components/status"
import Comments from "../components/form-comments"
import ValidationErrors from "../components/form-errors"
import { LotGetter } from "transactions/hooks/use-transaction-list"

const EDITABLE = [LotStatus.Draft, LotStatus.ToFix]
const COMMENTABLE = [LotStatus.ToFix, LotStatus.Inbox]

type TransactionDetailsProps = {
  entity: EntitySelection
  deleter: LotDeleter
  validator: LotValidator
  acceptor: LotAcceptor
  rejector: LotRejector
  refresh: () => void
  transactions: LotGetter
}

const TransactionDetails = ({
  entity,
  deleter,
  validator,
  acceptor,
  rejector,
  refresh,
  transactions,
}: TransactionDetailsProps) => {
  const {
    form,
    hasChange,
    details,
    request,
    comment,
    status,
    fieldErrors,
    validationErrors,
    change,
    submit,
    close,
    addComment,
    refreshDetails,
  } = useTransactionDetails(entity, refresh)
  const relativePush = useRelativePush()

  const isEditable = EDITABLE.includes(status)
  const isCommentable = COMMENTABLE.includes(status)

  async function run(
    action: (i: number) => Promise<boolean>,
    closeOnDone: boolean = false
  ) {
    if (await action(form.id)) {
      refreshDetails()

      if (closeOnDone) {
        close()
      }
    }
  }

  let previousTransactionId: number | null = null
  let nextTransactionId: number | null = null

  if (transactions?.data) {
    for (let i = 0; i < transactions.data.lots.length; i++) {
      let lot = transactions.data.lots[i]
      if (lot.id === details.data?.transaction.id) {
        previousTransactionId = i > 0 ? transactions.data.lots[i - 1].id : null // prettier-ignore
        nextTransactionId = i + 1 < transactions.data.lots.length ? transactions.data.lots[i + 1].id : null // prettier-ignore
      }
    }
  }

  return (
    <Modal onClose={close}>
      <StatusTitle editable={isEditable} details={details.data} entity={entity}>
        Détails de la transaction
      </StatusTitle>

      <TransactionForm
        id="transaction-details"
        entity={entity}
        readOnly={!isEditable}
        transaction={form}
        error={details.error ?? request.error}
        fieldErrors={fieldErrors}
        onChange={change}
      />

      {validationErrors.length > 0 && (
        <ValidationErrors validationErrors={validationErrors} />
      )}

      {details.data && details.data.comments.length > 0 && (
        <Comments
          readOnly={!isCommentable}
          loading={comment.loading}
          comments={details.data.comments}
          onComment={addComment}
        />
      )}

      <div className={styles.transactionFormButtons}>
        {isEditable && (
          <AsyncButton
            disabled={!hasChange}
            submit="transaction-details"
            icon={Save}
            level="primary"
            loading={request.loading}
            onClick={submit}
          >
            Sauvegarder
          </AsyncButton>
        )}

        {status === LotStatus.Draft && (
          <AsyncButton
            disabled={hasChange}
            icon={Check}
            level="success"
            loading={validator.loading}
            onClick={() => run(validator.validateLot)}
          >
            Envoyer
          </AsyncButton>
        )}

        {status === LotStatus.ToFix && (
          <AsyncButton
            disabled={hasChange}
            icon={Check}
            level="success"
            loading={validator.loading}
            onClick={() => run(validator.validateAndCommentLot)}
          >
            Renvoyer
          </AsyncButton>
        )}

        {isEditable && (
          <AsyncButton
            icon={Cross}
            level="danger"
            loading={deleter.loading}
            onClick={() => run(deleter.deleteLot, true)}
          >
            Supprimer
          </AsyncButton>
        )}

        {status === LotStatus.Inbox && (
          <React.Fragment>
            <AsyncButton
              icon={Check}
              level="success"
              loading={acceptor.loading}
              onClick={() => run(acceptor.acceptLot)}
            >
              Accepter
            </AsyncButton>
            <AsyncButton
              icon={AlertTriangle}
              level="warning"
              loading={acceptor.loading}
              onClick={() => run(acceptor.acceptAndCommentLot)}
            >
              Accepter sous réserve
            </AsyncButton>
            <AsyncButton
              icon={Cross}
              level="danger"
              loading={rejector.loading}
              onClick={() => run(rejector.rejectLot, true)}
            >
              Refuser
            </AsyncButton>
          </React.Fragment>
        )}

        <Box row className={styles.transactionNavButtons}>
          <Button
            icon={ChevronLeft}
            disabled={!previousTransactionId}
            onClick={() => relativePush(`../${previousTransactionId}`)}
          >
            Lot Précédent
          </Button>

          <Button
            icon={ChevronRight}
            disabled={!nextTransactionId}
            onClick={() => relativePush(`../${nextTransactionId}`)}
          >
            Lot Suivant
          </Button>

          <Button icon={Return} onClick={close}>
            Retour
          </Button>
        </Box>
      </div>

      {details.loading && <LoaderOverlay />}
    </Modal>
  )
}

export default TransactionDetails
