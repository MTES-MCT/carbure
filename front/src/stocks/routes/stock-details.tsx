import React from "react"
import { useTranslation } from 'react-i18next'

import { LotStatus, Transaction, UserRole } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotAcceptor } from "transactions/hooks/actions/use-accept-lots"
import { LotRejector } from "transactions/hooks/actions/use-reject-lots"
import { LotValidator } from "transactions/hooks/actions/use-validate-lots"
import { LotSender } from "stocks/hooks/use-send-lots"

import styles from "transactions/components/form.module.css"

import useStockDetails from "../hooks/use-stock-details"
import Modal from "common/components/modal"
import {
  Check,
  ChevronLeft,
  ChevronRight,
  Cross,
  Edit,
  Return,
  Save,
} from "common/components/icons"
import { Box, LoaderOverlay } from "common/components"
import { AsyncButton, Button } from "common/components/button"
import TransactionForm from "transactions/components/form"
import ValidationErrors from "transactions/components/form-errors"
import { StatusTitle } from "transactions/components/status"
import Comments from "transactions/components/form-comments"
import { useRights } from "carbure/hooks/use-rights"
import { Trans } from "react-i18next"
import useNavigation from "transactions/hooks/query/use-navigate"

const EDITABLE = [LotStatus.ToSend]

type StockDetailsProps = {
  entity: EntitySelection
  deleter: LotDeleter
  validator: LotValidator
  acceptor: LotAcceptor
  rejector: LotRejector
  sender: LotSender
  transactions: number[]
  refresh: () => void
}

const StockDetails = ({
  entity,
  deleter,
  acceptor,
  rejector,
  sender,
  transactions,
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

  const { t } = useTranslation()
  const rights = useRights()
  const navigator = useNavigation(transactions)

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)
  const isEditable = EDITABLE.includes(status)
  const transaction = details.data?.transaction

  async function run(
    action: (tx: Transaction) => Promise<boolean>,
    closeOnDone: boolean = false
  ) {
    if (transaction && (await action(transaction))) {
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
        <Trans>Détails du stock</Trans>
      </StatusTitle>

      <TransactionForm
        id="stock-details"
        entity={entity}
        readOnly={!isEditable || !canModify}
        transaction={form}
        error={details.error ?? request.error}
        errors={fieldErrors}
        onChange={change}
      />

      {(validationErrors.length > 0 || Object.keys(fieldErrors).length > 0) && (
        <ValidationErrors errors={validationErrors} />
      )}

      {details.data && details.data.comments.length > 0 && (
        <Comments
          readOnly
          title={t("Commentaires")}
          loading={details.loading}
          comments={details.data.comments}
        />
      )}

      <div className={styles.transactionFormButtons}>
        {canModify && isEditable && (
          <AsyncButton
            disabled={!hasChange}
            submit="stock-details"
            icon={Save}
            level="primary"
            loading={request.loading}
            onClick={submit}
          >
            <Trans>Sauvegarder</Trans>
          </AsyncButton>
        )}

        {canModify && status === LotStatus.Inbox && (
          <React.Fragment>
            <AsyncButton
              icon={Check}
              level="success"
              loading={acceptor.loading}
              onClick={() => run(acceptor.acceptLot)}
            >
              <Trans>Accepter</Trans>
            </AsyncButton>
            <AsyncButton
              icon={Cross}
              level="danger"
              loading={rejector.loading}
              onClick={() => run(rejector.rejectLot, true)}
            >
              <Trans>Refuser</Trans>
            </AsyncButton>
          </React.Fragment>
        )}

        {canModify && status === LotStatus.Stock && (
          <React.Fragment>
            <AsyncButton
              icon={Edit}
              level="primary"
              loading={acceptor.loading}
              onClick={() => run(sender.createDrafts, true)}
            >
              <Trans>Préparer l'envoi</Trans>
            </AsyncButton>
          </React.Fragment>
        )}

        {canModify && status === LotStatus.ToSend && (
          <React.Fragment>
            <AsyncButton
              disabled={hasChange}
              icon={Check}
              level="success"
              loading={sender.loading}
              onClick={() => run(sender.sendLot)}
            >
              <Trans>Envoyer</Trans>
            </AsyncButton>
            <AsyncButton
              icon={Cross}
              level="danger"
              loading={deleter.loading}
              onClick={() => run(deleter.deleteLot, true)}
            >
              <Trans>Supprimer</Trans>
            </AsyncButton>
          </React.Fragment>
        )}

        <Box row className={styles.transactionNavButtons}>
          <Button
            icon={ChevronLeft}
            disabled={!navigator.hasPrev}
            onClick={navigator.prev}
          >
            <Trans>Lot Précédent</Trans>
          </Button>

          <Button
            icon={ChevronRight}
            disabled={!navigator.hasNext}
            onClick={navigator.next}
          >
            <Trans>Lot Suivant</Trans>
          </Button>

          <Button icon={Return} onClick={close}>
            <Trans>Retour</Trans>
          </Button>
        </Box>
      </div>

      {details.loading && <LoaderOverlay />}
    </Modal>
  )
}

export default StockDetails
