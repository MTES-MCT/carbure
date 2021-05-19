import React from "react"

import { LotStatus } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotAcceptor } from "transactions/hooks/actions/use-accept-lots"
import { LotRejector } from "transactions/hooks/actions/use-reject-lots"
import { LotValidator } from "transactions/hooks/actions/use-validate-lots"

import styles from "../components/form.module.css"

import useTransactionDetails from "../hooks/use-transaction-details"
import useNavigate from "../hooks/query/use-navigate"

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

const EDITABLE = [LotStatus.Draft, LotStatus.ToFix]
const COMMENTABLE = [LotStatus.ToFix, LotStatus.Inbox]

type TransactionDetailsProps = {
  entity: EntitySelection
  deleter: LotDeleter
  validator: LotValidator
  acceptor: LotAcceptor
  rejector: LotRejector
  transactions: number[]
  refresh: () => void
}

const TransactionDetails = ({
  entity,
  deleter,
  validator,
  acceptor,
  rejector,
  transactions,
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
    transaction,
    change,
    submit,
    close,
    addComment,
    refreshDetails,
  } = useTransactionDetails(entity, refresh)

  const navigator = useNavigate(transactions)

  const isEditable = EDITABLE.includes(status)
  const isCommentable = COMMENTABLE.includes(status)

  const hasErrors =
    validationErrors.length > 0 || Object.keys(fieldErrors).length > 0

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

  return (
    <Modal onClose={close}>
      <StatusTitle editable={isEditable} details={details.data} entity={entity}>
        Détails de la transaction {form.carbure_id}
      </StatusTitle>

      <TransactionForm
        id="transaction-details"
        entity={entity}
        readOnly={!isEditable}
        transaction={form}
        error={details.error ?? request.error}
        errors={fieldErrors}
        onChange={change}
      />

      {hasErrors && <ValidationErrors errors={validationErrors} />}

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

        {status === LotStatus.Inbox && transaction?.delivery_status !== "AC" && (
          <React.Fragment>
            <AsyncButton
              icon={Check}
              level="success"
              loading={acceptor.loading}
              onClick={() => run(acceptor.acceptLot)}
            >
              Accepter
            </AsyncButton>

            {!transaction?.lot.parent_lot && (
              <AsyncButton
                icon={AlertTriangle}
                level="warning"
                loading={acceptor.loading}
                onClick={() => run(acceptor.acceptAndCommentLot)}
              >
                Accepter sous réserve
              </AsyncButton>
            )}

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
            disabled={!navigator.hasPrev}
            onClick={navigator.prev}
          >
            Lot Précédent
          </Button>

          <Button
            icon={ChevronRight}
            disabled={!navigator.hasNext}
            onClick={navigator.next}
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
