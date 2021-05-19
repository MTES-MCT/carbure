import React from "react"
import format from "date-fns/format"
import fr from "date-fns/locale/fr"

import {
  Entity,
  LotStatus,
  TransactionQuery,
  TransactionSummary,
} from "common/types"
import { SortingSelection } from "transactions/hooks/query/use-sort-by" // prettier-ignore
import { PageSelection } from "common/components/pagination"

import { LotGetter } from "../hooks/use-transaction-list"
import { LotUploader } from "transactions/hooks/actions/use-upload-file"
import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotValidator } from "transactions/hooks/actions/use-validate-lots"
import { LotDuplicator } from "transactions/hooks/actions/use-duplicate-lots"
import { LotAcceptor } from "transactions/hooks/actions/use-accept-lots"
import { LotRejector } from "transactions/hooks/actions/use-reject-lots"
import { StatusSelection } from "transactions/hooks/query/use-status"
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { SpecialSelection } from "transactions/hooks/query/use-special"
import { FilterSelection } from "transactions/hooks/query/use-filters"

import { AlertCircle } from "common/components/icons"
import { Box, LoaderOverlay } from "common/components"
import { Alert } from "common/components/alert"
import Pagination from "common/components/pagination"
import { TransactionTable } from "./list-table"

import styles from "./list.module.css"

import {
  ActionBar,
  DraftActions,
  ProducerImportActions,
  OperatorImportActions,
  ExportActions,
  InboxActions,
  ToFixActions,
  TraderImportActions,
  CreateActions,
} from "./list-actions"
import {
  DeadlineFilter,
  InvalidFilter,
  SummaryFilter,
} from "./list-special-filters"
import { OperatorOutsourcedBlendingActions } from "./list-actions"
import { LotForwarder } from "transactions/hooks/actions/use-forward-lots"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { SearchSelection } from "transactions/hooks/query/use-search"
import { ApiState } from "common/hooks/use-api"

type TransactionListProps = {
  entity: Entity
  transactions: LotGetter
  filters: FilterSelection
  status: StatusSelection
  sorting: SortingSelection
  special: SpecialSelection
  selection: TransactionSelection
  pagination: PageSelection
  search: SearchSelection
  query: TransactionQuery
  deleter: LotDeleter
  uploader: LotUploader
  validator: LotValidator
  duplicator: LotDuplicator
  acceptor: LotAcceptor
  rejector: LotRejector
  outsourceddepots: EntityDeliverySite[] | undefined
  forwarder: LotForwarder
  summary: ApiState<TransactionSummary>
}

export const TransactionList = ({
  entity,
  transactions,
  filters,
  status,
  sorting,
  special,
  selection,
  pagination,
  search,
  query,
  deleter,
  uploader,
  validator,
  duplicator,
  acceptor,
  rejector,
  outsourceddepots,
  forwarder,
  summary,
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
  const isAdmin = entity.entity_type === "Administration"

  const isLoading = transactions.loading
  const isError = transactions.error !== null
  const isEmpty = txs === null || txs.lots.length === 0

  const hasOutsourcedBlendingDepot =
    outsourceddepots && outsourceddepots.length > 0

  return (
    <Box className={styles.transactionList}>
      {isError && (
        <Alert level="error" icon={AlertCircle}>
          {transactions.error}
          {isLoading && <LoaderOverlay />}
        </Alert>
      )}

      {!isError && (
        <ActionBar search={search}>
          <ExportActions
            isEmpty={isEmpty}
            onExportAll={transactions.exportAllTransactions}
          />

          {status.is(LotStatus.Draft) && (
            <React.Fragment>
              {isProducer && <ProducerImportActions uploader={uploader} />}
              {isTrader && <TraderImportActions uploader={uploader} />}
              {isOperator && <OperatorImportActions uploader={uploader} />}
            </React.Fragment>
          )}

          {status.is(LotStatus.Draft) && (
            <React.Fragment>
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
            <React.Fragment>
              <InboxActions
                disabled={isEmpty}
                hasSelection={selection.selected.length > 0}
                acceptor={acceptor}
                rejector={rejector}
              />
            </React.Fragment>
          )}

          {status.is(LotStatus.ToFix) && (
            <ToFixActions
              disabled={selection.selected.length === 0}
              deleter={deleter}
            />
          )}

          {isOperator &&
            hasOutsourcedBlendingDepot &&
            status.is(LotStatus.Accepted) && (
              <OperatorOutsourcedBlendingActions
                forwarder={forwarder}
                outsourceddepots={outsourceddepots}
                disabled={selection.selected.length === 0 ? true : false}
                selection={selection}
              />
            )}
        </ActionBar>
      )}

      {!isEmpty && !isAdmin && (
        <SummaryFilter
          loading={summary.loading}
          txCount={summary.data?.tx_ids.length ?? 0}
          totalVolume={summary.data?.total_volume ?? 0}
          query={query}
          selection={selection.selected}
          hideRecap={isAdmin}
          onReset={() => {
            filters.reset()
            selection.reset()
            search.setQuery("")
          }}
        />
      )}

      {!special.deadline &&
        errorCount > 0 &&
        !status.is(LotStatus.Accepted) && (
          <InvalidFilter
            loading={isLoading}
            errorCount={errorCount}
            special={special}
          />
        )}

      {!special.invalid && deadlineCount > 0 && (
        <DeadlineFilter
          loading={isLoading}
          deadlineCount={deadlineCount}
          deadlineDate={deadlineDate}
          special={special}
          entity={entity}
        />
      )}

      {!isError && isEmpty && (
        <Alert level="warning" icon={AlertCircle}>
          Aucune transaction trouvée pour cette recherche
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
              sorting={sorting}
              outsourceddepots={outsourceddepots}
              selection={selection}
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
