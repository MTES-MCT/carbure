import React from "react"
import cl from "clsx"

import styles from "./transaction-actions.module.css"

import { LotDeleter } from "../hooks/actions/use-delete-lots"
import { LotUploader } from "../hooks/actions/use-upload-file"
import { LotValidator } from "../hooks/actions/use-validate-lots"
import { Link } from "./relative-route"
import { AsyncButton, Box, Button } from "./system"
import { Check, Cross, Download, Plus, Rapport, Upload } from "./system/icons"

type ExportActionProps = {
  isEmpty: boolean
  onExportAll: () => void
}

export const ExportAction = ({ isEmpty, onExportAll }: ExportActionProps) => (
  <Button icon={Download} disabled={isEmpty} onClick={onExportAll}>
    Exporter
  </Button>
)

type DraftActionProps = {
  disabled: boolean
  hasSelection: boolean
  uploader: LotUploader
  deleter: LotDeleter
  validator: LotValidator
}

export const DraftLotsActions = ({
  disabled,
  hasSelection,
  uploader,
  deleter,
  validator,
}: DraftActionProps) => {
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

  return (
    <React.Fragment>
      <AsyncButton as="label" icon={Upload} loading={uploader.loading}>
        Importer lots
        <input
          type="file"
          style={{ display: "none" }}
          onChange={(e) => uploader.uploadFile(e!.target.files![0])}
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

export const ValidatedLotsActions = () => (
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

export const ActionBar = ({ children }: { children: React.ReactNode }) => (
  <Box row className={cl(styles.actionBar)}>
    {children}
  </Box>
)
