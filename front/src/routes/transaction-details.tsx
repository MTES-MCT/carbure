import React from "react"

import { LotStatus } from "../services/types"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { LotDeleter } from "../hooks/actions/use-delete-lots"
import { LotAcceptor } from "../hooks/actions/use-accept-lots"
import { LotRejector } from "../hooks/actions/use-reject-lots"
import { LotValidator } from "../hooks/actions/use-validate-lots"

import styles from "../components/transaction-form.module.css"

import useTransactionDetails from "../hooks/use-transaction-details"

import {
  AlertTriangle,
  Check,
  Cross,
  Return,
  Save,
} from "../components/system/icons"
import { AsyncButton, Button, LoaderOverlay, Title } from "../components/system"
import { Collapsible } from "../components/system/alert"
import Modal from "../components/system/modal"
import Comments from "../components/comments"
import TransactionForm from "../components/transaction-form"

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

  async function run(action: (i: number) => Promise<boolean>) {
    if (await action(form.id)) {
      refresh()
      refreshDetails()
    }
  }

  return (
    <Modal onClose={close}>
      <Title>Transaction #{form.id ?? "N/A"}</Title>

      <TransactionForm
        id="transaction-details"
        readOnly={!isEditable}
        transaction={form}
        error={details.error ?? request.error}
        fieldErrors={fieldErrors}
        onChange={change}
      />

      {validationErrors.length > 0 && (
        <Collapsible
          level="error"
          title={`Erreurs (${validationErrors.length})`}
          className={styles.transactionError}
        >
          <ul className={styles.validationErrors}>
            {validationErrors.map((err, i) => (
              <li key={i}>{err.error || "Erreur de validation"}</li>
            ))}
          </ul>
        </Collapsible>
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
            icon={Check}
            level="success"
            loading={validator.loading}
            onClick={() => run(validator.validateAndCommentLot)}
          >
            Renvoyer
          </AsyncButton>
        )}

        {EDITABLE.includes(status) && (
          <AsyncButton
            icon={Cross}
            level="danger"
            loading={deleter.loading}
            onClick={() => run(deleter.deleteLot)}
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
              onClick={() => run(rejector.rejectLot)}
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
