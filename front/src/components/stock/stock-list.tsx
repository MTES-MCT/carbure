import React from "react"

import { LotStatus } from "../../services/types"
import { SortingSelection } from "../../hooks/query/use-sort-by" // prettier-ignore
import { PageSelection } from "../system/pagination"
import { StockHook } from "../../hooks/use-stock"

import { LotUploader } from "../../hooks/actions/use-upload-file"
import { LotDeleter } from "../../hooks/actions/use-delete-lots"
import { LotValidator } from "../../hooks/actions/use-validate-lots"
import { LotDuplicator } from "../../hooks/actions/use-duplicate-lots"
import { LotAcceptor } from "../../hooks/actions/use-accept-lots"
import { LotRejector } from "../../hooks/actions/use-reject-lots"
import { LotSender } from "../../hooks/actions/use-send-lots"
import { StatusSelection } from "../../hooks/query/use-status"
import { TransactionSelection } from "../../hooks/query/use-selection"

import styles from "./stock-list.module.css"

import { AlertCircle } from "../system/icons"
import { Box, LoaderOverlay } from "../system"
import { Alert } from "../system/alert"
import Pagination from "../system/pagination"
import { StockTable } from "./stock-table"

import {
  ActionBar,
  DraftActions,
  ExportActions,
  InboxActions,
  InboxSummaryActions,
} from "../transaction/transaction-actions"

import {
  StockActions,
  StockImportActions,
} from "./stock-actions"

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
  validator,
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
            <DraftActions
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
