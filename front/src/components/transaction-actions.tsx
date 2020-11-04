import React from "react"
import cl from "clsx"

import styles from "./transaction-actions.module.css"

import { LotDeleter } from "../hooks/actions/use-delete-lots"
import { LotUploader } from "../hooks/actions/use-upload-file"
import { LotValidator } from "../hooks/actions/use-validate-lots"
import { LotAcceptor } from "../hooks/actions/use-accept-lots"
import { LotRejector } from "../hooks/actions/use-reject-lots"

import { Link } from "./relative-route"
import { AsyncButton, Box, Button } from "./system"
import { Check, Cross, Download, Plus, Rapport, Upload } from "./system/icons"
import { prompt, PromptFormProps } from "./system/dialog"

type ExportActionsProps = {
  isEmpty: boolean
  onExportAll: () => void
}

export const ExportActions = ({ isEmpty, onExportAll }: ExportActionsProps) => (
  <Button icon={Download} disabled={isEmpty} onClick={onExportAll}>
    Exporter
  </Button>
)

type DraftActionsProps = {
  disabled: boolean
  hasSelection: boolean
  uploader: LotUploader
  deleter: LotDeleter
  validator: LotValidator
}

const ImportPromptFactory = (uploader: LotUploader) => ({
  onConfirm,
  onCancel,
}: PromptFormProps<File>) => (
  <Box style={{ maxWidth: 480 }}>
    <Box className={styles.importExplanation}>
      Le modèle simplifié vous permet de créer des lots provenant de vos propres
      usines. Vous pouvez les affilier immédiatement à des clients enregistrés
      sur Carbure ou simplement les ajouter à votre Mass Balance.
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateSimple}
      >
        Télécharger le modèle simplifié
      </span>
    </Box>

    <Box className={styles.importExplanation}>
      Le modèle avancé permet d'importer dans Carbure des lots achetés auprès de
      fournisseurs qui nous sont inconnus (fournisseurs étrangers ou producteurs
      français captifs). Vous avez également la possibilité d'attribuer ces lots
      à des clients étrangers.
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateAdvanced}
      >
        Télécharger le modèle avancé
      </span>
    </Box>

    <Box row className={styles.dialogButtons}>
      <Button as="label" level="primary" icon={Upload}>
        Importer lots
        <input
          type="file"
          style={{ display: "none" }}
          onChange={(e) => onConfirm(e!.target.files![0])}
        />
      </Button>
      <Button onClick={onCancel}>Annuler</Button>
    </Box>
  </Box>
)

const StockImportPromptFactory = (uploader: LotUploader) => ({
  onConfirm,
  onCancel,
}: PromptFormProps<File>) => (
  <Box style={{ maxWidth: 480 }}>
    <Box className={styles.importExplanation}>
      Ce modèle vous permet de créer des lots à partir de votre Mass Balance (onglet Lots en Stock)
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateMassBalance}
      >
        Télécharger le modèle
      </span>
    </Box>

    <Box row className={styles.dialogButtons}>
      <Button as="label" level="primary" icon={Upload}>
        Importer lots
        <input
          type="file"
          style={{ display: "none" }}
          onChange={(e) => onConfirm(e!.target.files![0])}
        />
      </Button>
      <Button onClick={onCancel}>Annuler</Button>
    </Box>
  </Box>
)


export const DraftActions = ({
  disabled,
  hasSelection,
  uploader,
  deleter,
  validator,
}: DraftActionsProps) => {
  function onValidate() {
    if (hasSelection) {
      validator.validateSelection()
    } else {
      validator.validateAllDrafts()
    }
  }

  function onDelete() {
    if (hasSelection) {
      deleter.deleteSelection()
    } else {
      deleter.deleteAllDrafts()
    }
  }

  async function onUpload() {
    const file = await prompt(
      "Import Excel",
      "Importer un fichier Excel standardisé.",
      ImportPromptFactory(uploader)
    )

    if (file) {
      uploader.uploadFile(file)
    }
  }

  return (
    <React.Fragment>
      <AsyncButton icon={Upload} loading={uploader.loading} onClick={onUpload}>
        Importer lots
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

export const StockDraftActions = ({
  disabled,
  hasSelection,
  uploader,
  deleter,
  validator,
}: DraftActionsProps) => {
  function onValidate() {
    if (hasSelection) {
      validator.validateSelection()
    } else {
      validator.validateAllDrafts()
    }
  }

  function onDelete() {
    if (hasSelection) {
      deleter.deleteSelection()
    } else {
      deleter.deleteAllDrafts()
    }
  }

  async function onUpload() {
    const file = await prompt(
      "Import Excel",
      "Importer un fichier Excel standardisé.",
      StockImportPromptFactory(uploader)
    )

    if (file) {
      uploader.uploadMassBalanceFile(file)
    }
  }

  return (
    <React.Fragment>
      <AsyncButton icon={Upload} loading={uploader.loading} onClick={onUpload}>
        Importer lots
      </AsyncButton>

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

export const OutSummaryActions = () => (
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

export const InboxSummaryActions = () => (
  <Link relative to="show-summary-in">
    <Button
      className={styles.transactionButtons}
      level="primary"
      icon={Rapport}
    >
      Rapport d'entrées
    </Button>
  </Link>
)

export const StockActions = () => (
  <Link relative to="send-complex">
    <Button
      className={styles.transactionButtons}
      level="primary"
      icon={Rapport}
    >
      Envoi complexe
    </Button>
  </Link>
)

export const ActionBar = ({ children }: { children: React.ReactNode }) => (
  <Box row className={cl(styles.actionBar)}>
    {children}
  </Box>
)
