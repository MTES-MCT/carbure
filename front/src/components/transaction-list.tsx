import React from "react"
import format from "date-fns/format"
import fr from "date-fns/locale/fr"

import { Entity, LotStatus } from "../services/types"
import { SortingSelection } from "../hooks/query/use-sort-by" // prettier-ignore
import { PageSelection } from "./system/pagination"
import { StockHook } from "../hooks/use-stock"

import { LotGetter } from "../hooks/use-transactions"
import { LotUploader } from "../hooks/actions/use-upload-file"
import { LotDeleter } from "../hooks/actions/use-delete-lots"
import { LotValidator } from "../hooks/actions/use-validate-lots"
import { LotDuplicator } from "../hooks/actions/use-duplicate-lots"
import { LotAcceptor } from "../hooks/actions/use-accept-lots"
import { LotRejector } from "../hooks/actions/use-reject-lots"
import { StatusSelection } from "../hooks/query/use-status"
import { TransactionSelection } from "../hooks/query/use-selection"
import { SpecialSelection } from "../hooks/query/use-special"

import styles from "./transaction-list.module.css"

import { AlertCircle, Calendar } from "./system/icons"
import { Box, LoaderOverlay } from "./system"
import { Alert, AlertFilter } from "./system/alert"
import Pagination from "./system/pagination"
import { TransactionTable, StockTable } from "./transaction-table"

import {
  ActionBar,
  ProducerDraftActions,
  OperatorDraftActions,
  ExportActions,
  OutSummaryActions,
  InboxActions,
  InboxSummaryActions,
  ToFixActions,
  StockActions,
  StockDraftActions,
} from "./transaction-actions"

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
          {((isOperator || isTrader) && status.is(LotStatus.Inbox)) && <InboxSummaryActions />}

          {(isProducer || isTrader) && status.is(LotStatus.Draft) && (
            <ProducerDraftActions
              disabled={isEmpty}
              hasSelection={selection.selected.length > 0}
              uploader={uploader}
              deleter={deleter}
              validator={validator}
            />
          )}

          {isOperator && status.is(LotStatus.Draft) && (
            <OperatorDraftActions
              disabled={isEmpty}
              hasSelection={selection.selected.length > 0}
              uploader={uploader}
              deleter={deleter}
              validator={validator}
            />
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

      {errorCount > 0 && (
        <AlertFilter
          level="error"
          icon={AlertCircle}
          active={special.invalid}
          onActivate={() => special.setInvalid(true)}
          onDispose={() => special.setInvalid(false)}
        >
          {errorCount === 1 ? (
            <span>
              <b>1 lot</b> présente des <b>incohérences</b>
            </span>
          ) : (
            <span>
              <b>{errorCount} lots</b> présentent des <b>incohérences</b>
            </span>
          )}
        </AlertFilter>
      )}

      {deadlineCount > 0 && (
        <AlertFilter
          level="warning"
          icon={Calendar}
          active={special.deadline}
          onActivate={() => special.setDeadline(true)}
          onDispose={() => special.setDeadline(false)}
        >
          {deadlineCount === 1 ? (
            <span>
              <b>1 lot</b> doit être validé et envoyé avant le{" "}
              <b>{deadlineDate}</b>
            </span>
          ) : (
            <span>
              <b>{deadlineCount} lots</b> doivent être validés et envoyés avant
              le <b>{deadlineDate}</b>
            </span>
          )}
        </AlertFilter>
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

type StockListProps = {
  stock: StockHook
  sorting: SortingSelection
  pagination: PageSelection
  status: StatusSelection
  selection: TransactionSelection
  deleter: LotDeleter
  uploader: LotUploader
  validator: LotValidator
  acceptor: LotAcceptor
  rejector: LotRejector
  duplicator: LotDuplicator
}

export const StockList = ({
  stock,
  sorting,
  pagination,
  status,
  selection,
  deleter,
  uploader,
  validator,
  acceptor,
  rejector,
  duplicator,
}: StockListProps) => {
  const txs = stock.data

  const isLoading = stock.loading
  const isError = typeof stock.error === "string"
  const isEmpty = txs === null || txs.lots.length === 0

  return (
    <Box className={styles.transactionList}>
      {isError && (
        <Alert level="error" icon={AlertCircle}>
          {stock.error}
        </Alert>
      )}

      {!isError && (
        <ActionBar>
          <ExportActions
            isEmpty={isEmpty}
            onExportAll={stock.exportAllTransactions}
          />

          {status.is(LotStatus.Inbox) && <InboxSummaryActions />}

          {status.is(LotStatus.Draft) && (
            <StockDraftActions
              disabled={isEmpty}
              hasSelection={selection.selected.length > 0}
              uploader={uploader}
              deleter={deleter}
              validator={validator}
            />
          )}

          {status.is(LotStatus.Inbox) && (
            <InboxActions
              disabled={isEmpty}
              hasSelection={selection.selected.length > 0}
              acceptor={acceptor}
              rejector={rejector}
            />
          )}

          {status.is(LotStatus.Stock) && <StockActions />}
        </ActionBar>
      )}

      {!isError && isEmpty && (
        <Alert level="warning" icon={AlertCircle}>
          Aucune transaction trouvée pour ces paramètres
        </Alert>
      )}

      {!isError && !isEmpty && (
        <React.Fragment>
          <Box>
            <StockTable
              stock={txs!}
              sorting={sorting}
              status={status}
              selection={selection}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={txs!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}
