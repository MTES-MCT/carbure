import React from "react"
import IframeResizer from "iframe-resizer-react"
import { stringify } from "querystring"

import {
  Entity,
  EntityType,
  LotStatus,
  TransactionQuery,
  TransactionSummary,
  UserRole,
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
import { Alert, Collapsible } from "common/components/alert"
import Pagination from "common/components/pagination"
import { TransactionTable } from "./list-table"

import { API_ROOT, filterParams } from "common/services/api"

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
  AuditorActions,
  AdminActions,
  CorrectionActions,
} from "./list-actions"
import {
  DeadlineFilter,
  InvalidFilter,
  SummaryFilter,
  NoResult,
} from "./list-special-filters"
import { OperatorOutsourcedBlendingActions } from "./list-actions"
import { LotForwarder } from "transactions/hooks/actions/use-forward-lots"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { SearchSelection } from "transactions/hooks/query/use-search"
import { ApiState } from "common/hooks/use-api"
import { useRights } from "carbure/hooks/use-rights"
import { LotAuditor } from "transactions/hooks/actions/use-audits"
import { LotAdministrator } from "transactions/hooks/actions/use-admin-lots"
import { formatDate } from "settings/components/common"

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
  auditor: LotAuditor
  administrator: LotAdministrator
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
  auditor,
  administrator,
}: TransactionListProps) => {
  const rights = useRights()

  const txs = transactions.data
  const errorCount = txs?.total_errors ?? 0
  const deadlineCount = txs?.deadlines.total ?? 0

  const deadlineDate = txs
    ? formatDate(txs.deadlines.date, {
        month: "long",
        year: undefined,
      })
    : null

  const isProducer = entity.entity_type === EntityType.Producer
  const isOperator = entity.entity_type === EntityType.Operator
  const isTrader = entity.entity_type === EntityType.Trader
  const isAuditor = entity.entity_type === EntityType.Auditor
  const isAdmin = entity.entity_type === EntityType.Administration

  const isLoading = transactions.loading
  const isError = transactions.error !== null
  const isEmpty = txs === null || txs.lots.length === 0

  const hasOutsourcedBlendingDepot =
    outsourceddepots && outsourceddepots.length > 0

  const hasSelection = selection.selected.length > 0
  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)
  const filterCount = Object.values(filters.selected).filter(Boolean).length

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

          {canModify && status.is(LotStatus.Draft) && (
            <React.Fragment>
              {isProducer && <ProducerImportActions uploader={uploader} />}
              {isTrader && <TraderImportActions uploader={uploader} />}
              {isOperator && <OperatorImportActions uploader={uploader} />}

              <CreateActions />

              <DraftActions
                disabled={isEmpty}
                hasSelection={hasSelection}
                uploader={uploader}
                deleter={deleter}
                validator={validator}
              />
            </React.Fragment>
          )}

          {canModify && status.is(LotStatus.Inbox) && (
            <React.Fragment>
              <InboxActions
                disabled={isEmpty}
                hasSelection={hasSelection}
                acceptor={acceptor}
                rejector={rejector}
              />
            </React.Fragment>
          )}

          {canModify && status.is(LotStatus.ToFix) && (
            <ToFixActions disabled={!hasSelection} deleter={deleter} />
          )}

          {(status.is(LotStatus.Accepted) || status.is(LotStatus.Inbox) || status.is(LotStatus.Validated)) && (
            <CorrectionActions disabled={!hasSelection} acceptor={acceptor} />
          )}

          {isOperator &&
            hasOutsourcedBlendingDepot &&
            canModify &&
            status.is(LotStatus.Accepted) && (
              <OperatorOutsourcedBlendingActions
                forwarder={forwarder}
                outsourceddepots={outsourceddepots}
                disabled={!hasSelection}
                selection={selection}
              />
            )}

          {isAdmin && (
            <AdminActions
              disabled={!hasSelection}
              administrator={administrator}
            />
          )}

          {isAuditor && (
            <AuditorActions disabled={!hasSelection} auditor={auditor} />
          )}
        </ActionBar>
      )}

      {isAdmin && (
        <Collapsible title="Voir la carte" className={styles.collapsibleMap}>
          <iframe
          height="600"
          title="Votre empreinte carbone"
          src={`${API_ROOT}/admin/map?${stringify(filterParams(query))}`}
          frameBorder="0"
          allowTransparency
        />
        </Collapsible>
      )}

      {!isEmpty && (
        <SummaryFilter
          loading={summary.loading}
          txCount={summary.data?.tx_ids.length ?? 0}
          totalVolume={summary.data?.total_volume ?? 0}
          query={query}
          selection={selection.selected}
          entity={entity}
          filterCount={filterCount}
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
        <NoResult
          loading={isLoading}
          onReset={filters.reset}
          filterCount={filterCount}
        />
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
              onAuditorHide={auditor.hideLot}
              onAuditorHighlight={auditor.highlightLot}
              onAdminHide={administrator.markAsRead}
              onAdminHighlight={administrator.markForReview}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={txs!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}
