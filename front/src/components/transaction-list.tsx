import React from "react"
import cl from "clsx"

import { Lots, LotStatus } from "../services/types"
import { StatusSelection, TransactionSelection, SortingSelection, Deleter, Uploader, Validator } from "../hooks/use-transactions" // prettier-ignore
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import styles from "./transaction-list.module.css"

import {
  AlertCircle,
  Check,
  Cross,
  Rapport,
  Download,
  Upload,
  Plus,
} from "./system/icons"

import { Alert, AsyncButton, Box, Button, LoaderOverlay } from "./system"
import Pagination from "./system/pagination"
import TransactionTable from "./transaction-table"
import { Link } from "./relative-route"

type DraftActionProps = {
  disabled: boolean
  selection: TransactionSelection
  uploader: Uploader
  deleter: Deleter
  validator: Validator
}

const DraftLotsActions = ({
  disabled,
  selection,
  uploader,
  deleter,
  validator,
}: DraftActionProps) => {
  const hasSelection = selection.selected.length > 0

  function onValidate() {
    if (hasSelection) {
      validator.resolve(selection.selected)
    } else {
      validator.resolveAll()
    }
  }

  function onDelete() {
    if (hasSelection) {
      deleter.resolve(selection.selected)
    } else {
      deleter.resolveAll()
    }
  }

  return (
    <React.Fragment>
      <AsyncButton as="label" icon={Upload} loading={uploader.loading}>
        Importer fichier
        <input
          type="file"
          style={{ display: "none" }}
          onChange={(e) => uploader.resolve(e!.target.files![0])}
        />
      </AsyncButton>

      <Link relative to="add">
        <Button icon={Plus} level="primary">
          Créer lot
        </Button>
      </Link>

      <AsyncButton
        icon={Check}
        level="success"
        loading={validator.loading}
        disabled={disabled}
        onClick={onValidate}
      >
        Envoyer {hasSelection ? `sélection` : "tout"}
      </AsyncButton>

      <AsyncButton
        icon={Cross}
        level="danger"
        loading={deleter.loading}
        disabled={disabled}
        onClick={onDelete}
      >
        Supprimer {hasSelection ? `sélection` : "tout"}
      </AsyncButton>
    </React.Fragment>
  )
}

const ValidatedLotsActions = () => (
  <Link relative to="show-summary-out">
    <Button
      className={styles.transactionButtons}
      level="primary"
      icon={Rapport}
    >
      Rapport de sorties
    </Button>
  </Link>
)

const ActionBar = ({ children }: { children: React.ReactNode }) => (
  <Box row className={cl(styles.actionBar)}>
    {children}
  </Box>
)

type TransactionListProps = {
  transactions: ApiState<Lots>
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  pagination: PageSelection
  deleter: Deleter
  uploader: Uploader
  validator: Validator
  onDuplicate: (id: number) => void
  onExportAll: () => void
}

const TransactionList = ({
  transactions,
  status,
  sorting,
  selection,
  pagination,
  deleter,
  uploader,
  validator,
  onDuplicate,
  onExportAll,
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
        </Alert>
      )}

      {!isError && (
        <ActionBar>
          <Button icon={Download} disabled={isEmpty} onClick={onExportAll}>
            Exporter tout
          </Button>

          {status.active === LotStatus.Draft && (
            <DraftLotsActions
              disabled={isEmpty}
              selection={selection}
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
              onDuplicate={onDuplicate}
              onValidate={validator.resolve}
              onDelete={deleter.resolve}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}

export default TransactionList
