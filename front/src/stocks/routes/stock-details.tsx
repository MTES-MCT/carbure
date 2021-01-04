import React from "react"

import { LotStatus } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotAcceptor } from "transactions/hooks/actions/use-accept-lots"
import { LotRejector } from "transactions/hooks/actions/use-reject-lots"
import { LotValidator } from "transactions/hooks/actions/use-validate-lots"
import { LotSender } from "stocks/hooks/use-send-lots"

import styles from "transactions/components/form.module.css"

import useStockDetails from "../hooks/use-stock-details"
import Modal from "common/components/modal"
import { Check, Cross, Edit, Return, Save } from "common/components/icons"
import { LoaderOverlay } from "common/components"
import { AsyncButton, Button } from "common/components/button"
import TransactionForm from "transactions/components/form"
import ValidationErrors from "transactions/components/form-errors"
import { StatusTitle } from "transactions/components/status"

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
