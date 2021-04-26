import React from "react"
import cl from "clsx"

import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotUploader } from "transactions/hooks/actions/use-upload-file"
import { LotValidator } from "transactions/hooks/actions/use-validate-lots"
import { LotAcceptor } from "transactions/hooks/actions/use-accept-lots"
import { LotRejector } from "transactions/hooks/actions/use-reject-lots"

import { Link } from "common/components/relative-route"
import { Box } from "common/components"
import { AsyncButton, Button } from "common/components/button"
import {
  Check,
  Cross,
  Download,
  Plus,
  Rapport,
  Upload,
  Forward,
} from "common/components/icons"
import { prompt } from "common/components/dialog"

import {
  TraderImportPrompt,
  OperatorImportPrompt,
  ProducerImportPrompt,
} from "./import"
import { OperatorForwardPrompt } from "./forward"

import styles from "./list-actions.module.css"
import { LotForwarder } from "transactions/hooks/actions/use-forward-lots"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { TransactionSelection } from "transactions/hooks/query/use-selection"

type ExportActionsProps = {
  isEmpty: boolean
  onExportAll: () => void
}

export const ExportActions = ({ isEmpty, onExportAll }: ExportActionsProps) => (
  <Button icon={Download} disabled={isEmpty} onClick={onExportAll}>
    Exporter
  </Button>
)

type ImportActionsProps = {
  uploader: LotUploader
}

export const ProducerImportActions = ({ uploader }: ImportActionsProps) => {
  async function onUpload() {
    const file = await prompt<File>((resolve) => (
      <ProducerImportPrompt uploader={uploader} onResolve={resolve} />
    ))

    if (file) {
      uploader.uploadFile(file)
    }
  }

  return (
    <AsyncButton icon={Upload} loading={uploader.loading} onClick={onUpload}>
      Importer lots
    </AsyncButton>
  )
}
export const TraderImportActions = ({ uploader }: ImportActionsProps) => {
  async function onUpload() {
    const file = await prompt<File>((resolve) => (
      <TraderImportPrompt uploader={uploader} onResolve={resolve} />
    ))

    if (file) {
      uploader.uploadFile(file)
    }
  }

  return (
    <AsyncButton icon={Upload} loading={uploader.loading} onClick={onUpload}>
      Importer lots
    </AsyncButton>
  )
}

export const OperatorImportActions = ({ uploader }: ImportActionsProps) => {
  async function onUpload() {
    const file = await prompt<File>((resolve) => (
      <OperatorImportPrompt uploader={uploader} onResolve={resolve} />
    ))

    if (file) {
      uploader.uploadOperatorFile(file)
    }
  }

  return (
    <AsyncButton icon={Upload} loading={uploader.loading} onClick={onUpload}>
      Importer lots
    </AsyncButton>
  )
}

export const CreateActions = () => (
  <Link relative to="add">
    <Button icon={Plus} level="primary">
      Créer lot
    </Button>
  </Link>
)

type DraftActionsProps = {
  disabled: boolean
  hasSelection: boolean
  uploader: LotUploader
  deleter: LotDeleter
  validator: LotValidator
}

export const DraftActions = ({
  disabled,
  hasSelection,
  deleter,
  validator,
}: DraftActionsProps) => {
  function onValidate() {
    if (hasSelection) {
      validator.validateSelection()
    } else {
      validator.validateAll()
    }
  }

  function onDelete() {
    if (hasSelection) {
      deleter.deleteSelection()
    } else {
      deleter.deleteAll()
    }
  }

  return (
    <React.Fragment>
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

type ToFixActionsProps = {
  disabled: boolean
  deleter: LotDeleter
}

export const ToFixActions = ({ disabled, deleter }: ToFixActionsProps) => {
  return (
    <AsyncButton
      icon={Cross}
      level="danger"
      loading={deleter.loading}
      disabled={disabled}
      onClick={deleter.deleteSelection}
    >
      Supprimer sélection
    </AsyncButton>
  )
}

type InboxActionsProps = {
  disabled: boolean
  hasSelection: boolean
  acceptor: LotAcceptor
  rejector: LotRejector
}

export const InboxActions = ({
  disabled,
  hasSelection,
  acceptor,
  rejector,
}: InboxActionsProps) => {
  function onAccept() {
    if (hasSelection) {
      acceptor.acceptSelection()
    } else {
      acceptor.acceptAllInbox()
    }
  }

  function onReject() {
    if (hasSelection) {
      rejector.rejectSelection()
    } else {
      rejector.rejectAllInbox()
    }
  }

  return (
    <React.Fragment>
      <AsyncButton
        icon={Check}
        level="success"
        loading={acceptor.loading}
        disabled={disabled}
        onClick={onAccept}
      >
        Accepter {hasSelection ? `sélection` : "tout"}
      </AsyncButton>

      <AsyncButton
        icon={Cross}
        level="danger"
        loading={rejector.loading}
        disabled={disabled}
        onClick={onReject}
      >
        Refuser {hasSelection ? `sélection` : "tout"}
      </AsyncButton>
    </React.Fragment>
  )
}

type OperatorOutsourcedBlendingProps = {
  disabled: boolean
  forwarder: LotForwarder
  outsourceddepots: EntityDeliverySite[] | undefined
  selection: TransactionSelection
}

export const OperatorOutsourcedBlendingActions = ({
  disabled,
  forwarder,
  outsourceddepots,
  selection,
}: OperatorOutsourcedBlendingProps) => {
  async function onForward() {
    const validated = await prompt<boolean>((resolve) => (
      <OperatorForwardPrompt
        outsourceddepots={outsourceddepots}
        onResolve={resolve}
      />
    ))

    if (validated) {
      forwarder.forwardSelection(selection, outsourceddepots)
    }
  }
  return (
    <Button
      disabled={disabled}
      level="primary"
      icon={Forward}
      onClick={onForward}
    >
      Transférer
    </Button>
  )
}

export const ActionBar = ({ children }: { children: React.ReactNode }) => (
  <Box row className={cl(styles.actionBar)}>
    {children}
  </Box>
)
