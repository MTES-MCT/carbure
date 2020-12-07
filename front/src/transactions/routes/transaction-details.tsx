import React from "react"

import { LotStatus } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import { LotDeleter } from "common/hooks/actions/use-delete-lots"
import { LotAcceptor } from "common/hooks/actions/use-accept-lots"
import { LotRejector } from "common/hooks/actions/use-reject-lots"
import { LotValidator } from "common/hooks/actions/use-validate-lots"

import styles from "../components/transaction-form.module.css"

import useTransactionDetails from "../hooks/use-transaction-details"

import {
  AlertTriangle,
  Check,
  Cross,
  Return,
  Save,
} from "common/components/icons"
import { AsyncButton, Button, LoaderOverlay } from "common/components"
import Modal from "common/components/modal"
import TransactionForm from "../components/transaction-form"
import { StatusTitle } from "../components/transaction-status"
import Comments from "../components/comments"
import ValidationErrors from "../components/validation-errors"

const EDITABLE = [LotStatus.Draft, LotStatus.ToFix]
const COMMENTABLE = [LotStatus.ToFix, LotStatus.Inbox]

type TransactionDetailsProps = {
  entity: EntitySelection
  deleter: LotDeleter
  validator: LotValidator
  acceptor: LotAcceptor
  rejector: LotRejector
  refresh: () => void
}

const TransactionDetails = ({
  entity,
  deleter,
  validator,
  acceptor,
  rejector,
  refresh,
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

  const isEditable = EDITABLE.includes(status)
  const isCommentable = COMMENTABLE.includes(status)

  async function run(
    action: (i: number) => Promise<boolean>,
    closeOnDone: boolean = false
  ) {
    if (await action(form.id)) {
      refresh()
      refreshDetails()

      if (closeOnDone) {
        close()
      }
    }
  }

  return (
    <Modal onClose={close}>
      <StatusTitle editable={isEditable} details={details.data}>
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

        <Button
          icon={Return}
          className={styles.transactionCloseButton}
          onClick={close}
        >
          Retour
        </Button>
      </div>

      {details.loading && <LoaderOverlay />}
    </Modal>
  )
}

export default TransactionDetails
