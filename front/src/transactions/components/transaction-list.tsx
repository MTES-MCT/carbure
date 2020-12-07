import React from "react"
import format from "date-fns/format"
import fr from "date-fns/locale/fr"

import { Entity, LotStatus } from "common/types"
import { SortingSelection } from "common/hooks/query/use-sort-by" // prettier-ignore
import { PageSelection } from "common/components/pagination"

import { LotGetter } from "../hooks/use-transactions"
import { LotUploader } from "common/hooks/actions/use-upload-file"
import { LotDeleter } from "common/hooks/actions/use-delete-lots"
import { LotValidator } from "common/hooks/actions/use-validate-lots"
import { LotDuplicator } from "common/hooks/actions/use-duplicate-lots"
import { LotAcceptor } from "common/hooks/actions/use-accept-lots"
import { LotRejector } from "common/hooks/actions/use-reject-lots"
import { StatusSelection } from "common/hooks/query/use-status"
import { TransactionSelection } from "common/hooks/query/use-selection"
import { SpecialSelection } from "common/hooks/query/use-special"

import styles from "./transaction-list.module.css"

import { AlertCircle } from "common/components/icons"
import { Box, LoaderOverlay } from "common/components"
import { Alert } from "common/components/alert"
import Pagination from "common/components/pagination"
import { TransactionTable } from "./transaction-table"

import {
  ActionBar,
  DraftActions,
  ProducerImportActions,
  OperatorImportActions,
  ExportActions,
  OutSummaryActions,
  InboxActions,
  InboxSummaryActions,
  ToFixActions,
  TraderImportActions,
  CreateActions,
} from "./transaction-actions"
import { DeadlineFilter, InvalidFilter } from "./special-filters"

type TransactionListProps = {
  entity: Entity
  transactions: LotGetter
  status: StatusSelection
  sorting: SortingSelection
  special: SpecialSelection
  selection: TransactionSelection
  pagination: PageSelection
  deleter: LotDeleter
  uploader: LotUploader
  validator: LotValidator
  duplicator: LotDuplicator
  acceptor: LotAcceptor
  rejector: LotRejector
}

export const TransactionList = ({
  entity,
  transactions,
  status,
  sorting,
  special,
  selection,
  pagination,
  deleter,
  uploader,
  validator,
  duplicator,
  acceptor,
  rejector,
}: TransactionListProps) => {
  const txs = transactions.data
  const errorCount = txs?.total_errors ?? 0
  const deadlineCount = txs?.deadlines.total ?? 0

  const deadlineDate = txs
    ? format(new Date(txs.deadlines.date), "d MMMM", { locale: fr })
    : null

  const isProducer = entity.entity_type === "Producteur"
  const isOperator = entity.entity_type === "Opérateur"
  const isTrader = entity.entity_type === "Trader"

  const isLoading = transactions.loading
  const isError = transactions.error !== null
  const isEmpty = txs === null || txs.lots.length === 0

  return (
    <Box className={styles.transactionList}>
      {isError && (
        <Alert level="error" icon={AlertCircle}>
          {transactions.error}
          {isLoading && <LoaderOverlay />}
        </Alert>
      )}

      {!isError && (
        <ActionBar>
          <ExportActions
            isEmpty={isEmpty}
            onExportAll={transactions.exportAllTransactions}
          />

          {status.is(LotStatus.Validated) && <OutSummaryActions />}

          {(isOperator || isTrader) && status.is(LotStatus.Inbox) && (
            <InboxSummaryActions />
          )}

          {status.is(LotStatus.Draft) && (
            <React.Fragment>
              {isProducer && <ProducerImportActions uploader={uploader} />}

              {isTrader && <TraderImportActions uploader={uploader} />}

              {isOperator && <OperatorImportActions uploader={uploader} />}

              <CreateActions />

              <DraftActions
                disabled={isEmpty}
                hasSelection={selection.selected.length > 0}
                uploader={uploader}
                deleter={deleter}
                validator={validator}
              />
            </React.Fragment>
          )}

          {status.is(LotStatus.Inbox) && (
            <InboxActions
              disabled={isEmpty}
              hasSelection={selection.selected.length > 0}
              acceptor={acceptor}
              rejector={rejector}
            />
          )}

          {status.is(LotStatus.ToFix) && (
            <ToFixActions
              disabled={selection.selected.length === 0}
              deleter={deleter}
            />
          )}
        </ActionBar>
      )}

      {!isLoading && !special.deadline && errorCount > 0 && (
        <InvalidFilter errorCount={errorCount} special={special} />
      )}

      {!isLoading && !special.invalid && deadlineCount > 0 && (
        <DeadlineFilter
          deadlineCount={deadlineCount}
          deadlineDate={deadlineDate}
          special={special}
          entity={entity}
        />
      )}

      {!isError && isEmpty && (
        <Alert level="warning" icon={AlertCircle}>
          Aucune transaction trouvée pour ces paramètres
          {isLoading && <LoaderOverlay />}
        </Alert>
      )}

      {!isError && !isEmpty && (
        <React.Fragment>
          <Box>
            <TransactionTable
              entity={entity}
              status={status}
              transactions={txs!}
              selection={selection}
              sorting={sorting}
              onDuplicate={duplicator.duplicateLot}
              onValidate={validator.validateLot}
              onDelete={deleter.deleteLot}
              onAccept={acceptor.acceptLot}
              onComment={acceptor.acceptAndCommentLot}
              onReject={rejector.rejectLot}
              onCorrect={validator.validateAndCommentLot}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={txs!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}
