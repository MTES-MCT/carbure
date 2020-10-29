import React from "react"

import { Lots, LotStatus } from "../services/types"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { ApiState } from "../hooks/helpers/use-api"
import { LotDeleter } from "../hooks/actions/use-delete-lots"
import { LotAcceptor } from "../hooks/actions/use-accept-lots"
import { LotRejector } from "../hooks/actions/use-reject-lots"
import { LotValidator } from "../hooks/actions/use-validate-lots"

import useTransactionDetails from "../hooks/use-transaction-details"

import Modal from "../components/system/modal"
import { AsyncButton, LoaderOverlay, Title } from "../components/system"
import { AlertTriangle, Check, Cross, Save } from "../components/system/icons"
import TransactionForm from "../components/transaction-form"

const EDITABLE = [LotStatus.Draft, LotStatus.ToFix]

type TransactionDetailsProps = {
  entity: EntitySelection
  transactions: ApiState<Lots>
  deleter: LotDeleter
  validator: LotValidator
  acceptor: LotAcceptor
  rejector: LotRejector
  refresh: () => void
}

const TransactionDetails = ({
  entity,
  transactions,
  deleter,
  validator,
  acceptor,
  rejector,
  refresh,
}: TransactionDetailsProps) => {
  const {
    form,
    request,
    status,
    fieldErrors,
    change,
    submit,
    close,
  } = useTransactionDetails(entity, transactions, refresh)

  async function run(
    action: (i: number) => Promise<boolean>,
    needSave = false
  ) {
    if (needSave) {
      await submit()
    }

    if (await action(form.id)) {
      close()
    }
  }

  return (
    <Modal onClose={close}>
      <Title>Transaction #{form.id ?? "N/A"}</Title>

      <TransactionForm
        status={status}
        readOnly={!EDITABLE.includes(status)}
        transaction={form}
        error={request.error}
        fieldErrors={fieldErrors}
        onChange={change}
        onClose={close}
      >
        {status === LotStatus.Draft && (
          <React.Fragment>
            <AsyncButton
              submit
              icon={Save}
              level="primary"
              loading={request.loading}
              onClick={submit}
            >
              Sauvegarder
            </AsyncButton>
            <AsyncButton
              submit
              icon={Check}
              level="success"
              loading={validator.loading}
              onClick={() => run(validator.validateLot, true)}
            >
              Envoyer
            </AsyncButton>
          </React.Fragment>
        )}

        {status === LotStatus.ToFix && (
          <AsyncButton
            submit
            icon={Check}
            level="success"
            loading={validator.loading}
            onClick={() => run(validator.validateAndCommentLot, true)}
          >
            Renvoyer
          </AsyncButton>
        )}

        {EDITABLE.includes(status) && (
          <AsyncButton
            submit
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
              submit
              icon={Check}
              level="success"
              loading={acceptor.loading}
              onClick={() => run(acceptor.acceptLot)}
            >
              Accepter
            </AsyncButton>
            <AsyncButton
              submit
              icon={AlertTriangle}
              level="warning"
              loading={acceptor.loading}
              onClick={() => run(acceptor.acceptAndCommentLot)}
            >
              Accepter sous réserve
            </AsyncButton>
            <AsyncButton
              submit
              icon={Cross}
              level="danger"
              loading={rejector.loading}
              onClick={() => run(rejector.rejectLot)}
            >
              Refuser
            </AsyncButton>
          </React.Fragment>
        )}
      </TransactionForm>

      {transactions.loading && <LoaderOverlay />}
    </Modal>
  )
}

export default TransactionDetails
