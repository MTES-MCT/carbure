import React from "react"

import { Lots, LotStatus } from "../services/types"
import { SortingSelection } from "../hooks/query/use-sort-by" // prettier-ignore
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import { LotGetter } from "../hooks/transactions/use-get-lots"
import { LotUploader } from "../hooks/actions/use-upload-file"
import { LotDeleter } from "../hooks/actions/use-delete-lots"
import { LotValidator } from "../hooks/actions/use-validate-lots"
import { LotDuplicator } from "../hooks/actions/use-duplicate-lots"
import { StatusSelection } from "../hooks/query/use-status"
import { TransactionSelection } from "../hooks/query/use-selection"

import styles from "./transaction-list.module.css"

import { AlertCircle } from "./system/icons"
import { Alert, Box, LoaderOverlay } from "./system"
import Pagination from "./system/pagination"
import { TransactionTable, StockTable } from "./transaction-table"

import {
  ActionBar,
  DraftLotsActions,
  ExportAction,
  ValidatedLotsActions,
} from "./transaction-actions"

type TransactionListProps = {
  transactions: LotGetter
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  pagination: PageSelection
  deleter: LotDeleter
  uploader: LotUploader
  validator: LotValidator
  duplicator: LotDuplicator
}

export const TransactionList = ({
  transactions,
  status,
  sorting,
  selection,
  pagination,
  deleter,
  uploader,
  validator,
  duplicator,
}: TransactionListProps) => {
  const tx = transactions.data

  const isLoading = transactions.loading
  const isError = typeof transactions.error === "string"
  const isEmpty = tx === null || tx.lots.length === 0

  return (
    <Box className={styles.transactionList}>
      {isError && (
        <Alert level="error">
          <AlertCircle />
          {transactions.error}
          {isLoading && <LoaderOverlay />}
        </Alert>
      )}

      {!isError && (
        <ActionBar>
          <ExportAction
            isEmpty={isEmpty}
            onExportAll={transactions.exportAllTransactions}
          />

          {status.active === LotStatus.Draft && (
            <DraftLotsActions
              disabled={isEmpty}
              hasSelection={selection.selected.length > 0}
              uploader={uploader}
              deleter={deleter}
              validator={validator}
            />
          )}

          {status.active === LotStatus.Validated && <ValidatedLotsActions />}
        </ActionBar>
      )}

      {!isError && isEmpty && (
        <Alert level="warning">
          <AlertCircle />
          Aucune transaction trouvée pour ces paramètres
          {isLoading && <LoaderOverlay />}
        </Alert>
      )}

      {!isError && !isEmpty && (
        <React.Fragment>
          <Box>
            <TransactionTable
              status={status}
              transactions={tx!}
              selection={selection}
              sorting={sorting}
              onDuplicate={duplicator.duplicateLot}
              onValidate={validator.validateLot}
              onDelete={deleter.deleteLot}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}

type StockListProps = {
  transactions: ApiState<Lots>
  sorting: SortingSelection
  pagination: PageSelection
}

export const StockList = ({
  transactions,
  sorting,
  pagination,
}: StockListProps) => {
  const tx = transactions.data

  const isLoading = transactions.loading
  const isError = typeof transactions.error === "string"
  const isEmpty = tx === null || tx.lots.length === 0

  return (
    <Box className={styles.transactionList}>
      {isError && (
        <Alert level="error">
          <AlertCircle />
          {transactions.error}
        </Alert>
      )}

      {!isError && isEmpty && (
        <Alert level="warning">
          <AlertCircle />
          Aucune transaction trouvée pour ces paramètres
        </Alert>
      )}

      {!isError && !isEmpty && (
        <React.Fragment>
          <Box>
            <StockTable transactions={tx!} sorting={sorting} />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}
