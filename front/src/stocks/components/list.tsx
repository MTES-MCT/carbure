import React from "react"

import { LotStatus } from "common/types"
import { SortingSelection } from "transactions/hooks/query/use-sort-by"
import { PageSelection } from "common/components/pagination"
import { LotUploader } from "transactions/hooks/actions/use-upload-file"
import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotValidator } from "transactions/hooks/actions/use-validate-lots"
import { LotDuplicator } from "transactions/hooks/actions/use-duplicate-lots"
import { LotAcceptor } from "transactions/hooks/actions/use-accept-lots"
import { LotRejector } from "transactions/hooks/actions/use-reject-lots"
import { LotSender } from "transactions/hooks/actions/use-send-lots"
import { StatusSelection } from "transactions/hooks/query/use-status"
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { StockHook } from "../hooks/use-stock-list"

import { AlertCircle } from "common/components/icons"
import { Box, LoaderOverlay } from "common/components"
import { Alert } from "common/components/alert"
import Pagination from "common/components/pagination"

import {
  ActionBar,
  ExportActions,
  InboxActions,
  InboxSummaryActions,
} from "transactions/components/list-actions"

import {
  StockActions,
  StockImportActions,
  StockDraftActions,
} from "./list-actions"
import { StockTable } from "./list-table"

import styles from "./list.module.css"

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
  sender: LotSender
}

export const StockList = ({
  stock,
  sorting,
  pagination,
  status,
  selection,
  deleter,
  uploader,
  acceptor,
  rejector,
  sender,
}: StockListProps) => {
  const txs = stock.data

  const isLoading = stock.loading
  const isError = typeof stock.error === "string"
  const isEmpty = txs === null || txs.lots.length === 0

  return (
    <Box className={styles.stockList}>
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

          {status.is(LotStatus.ToSend) && (
            <StockImportActions uploader={uploader} />
          )}

          {status.is(LotStatus.ToSend) && (
            <StockDraftActions
              disabled={isEmpty}
              hasSelection={selection.selected.length > 0}
              uploader={uploader}
              deleter={deleter}
              sender={sender}
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
              sender={sender}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={txs!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}
