import React from "react"

import { LotStatus } from "../../common/types"
import { EntitySelection } from "../../common/hooks/helpers/use-entity"
import { LotDeleter } from "../../common/hooks/actions/use-delete-lots"
import { LotAcceptor } from "../../common/hooks/actions/use-accept-lots"
import { LotRejector } from "../../common/hooks/actions/use-reject-lots"
import { LotValidator } from "../../common/hooks/actions/use-validate-lots"
import { LotSender } from "../../common/hooks/actions/use-send-lots"

import styles from "../../transactions/components/transaction-form.module.css"

import useStockDetails from "../hooks/use-stock-details"
import Modal from "../../common/system/modal"
import { Check, Cross, Edit, Return, Save } from "../../common/system/icons"
import { AsyncButton, Button, LoaderOverlay } from "../../common/system"
import TransactionForm from "../../transactions/components/transaction-form"
import ValidationErrors from "../../common/components/validation-errors"
import { StatusTitle } from "../../transactions/components/transaction-status"

const EDITABLE = [LotStatus.ToSend]

type StockDetailsProps = {
  entity: EntitySelection
  deleter: LotDeleter
  validator: LotValidator
  acceptor: LotAcceptor
  rejector: LotRejector
  sender: LotSender
  refresh: () => void
}

const StockDetails = ({
  entity,
  deleter,
  validator,
  acceptor,
  rejector,
  sender,
  refresh,
}: StockDetailsProps) => {
  const {
    form,
    hasChange,
    details,
    request,
    status,
    fieldErrors,
    validationErrors,
    change,
    submit,
    close,
    refreshDetails,
  } = useStockDetails(entity, refresh)

  const isEditable = EDITABLE.includes(status)

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
      <StatusTitle stock editable={isEditable} details={details.data}>
        Détails du stock
      </StatusTitle>

      <TransactionForm
        id="stock-details"
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

      <div className={styles.transactionFormButtons}>
        {isEditable && (
          <AsyncButton
            disabled={!hasChange}
            submit="stock-details"
            icon={Save}
            level="primary"
            loading={request.loading}
            onClick={submit}
          >
            Sauvegarder
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
              icon={Cross}
              level="danger"
              loading={rejector.loading}
              onClick={() => run(rejector.rejectLot, true)}
            >
              Refuser
            </AsyncButton>
          </React.Fragment>
        )}

        {status === LotStatus.Stock && (
          <React.Fragment>
            <AsyncButton
              icon={Edit}
              level="primary"
              loading={acceptor.loading}
              onClick={() => run(sender.createDrafts, true)}
            >
              Préparer l'envoi
            </AsyncButton>
          </React.Fragment>
        )}

        {status === LotStatus.ToSend && (
          <React.Fragment>
            <AsyncButton
              disabled={hasChange}
              icon={Check}
              level="success"
              loading={sender.loading}
              onClick={() => run(sender.sendLot)}
            >
              Envoyer
            </AsyncButton>
            <AsyncButton
              icon={Cross}
              level="danger"
              loading={deleter.loading}
              onClick={() => run(deleter.deleteLot, true)}
            >
              Supprimer
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

export default StockDetails
