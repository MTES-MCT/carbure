import React from "react"

import { Link } from "../../common/components/relative-route"
import {
  Check,
  Cross,
  Download,
  Plus,
  Rapport,
  Upload,
} from "../../common/system/icons"
import { AsyncButton, Button } from "../../common/system"
import { prompt } from "../../common/system/dialog"
import { StockImportPromptFactory } from "../../common/components/import-prompt"
import { LotUploader } from "../../common/hooks/actions/use-upload-file"
import { LotDeleter } from "../../common/hooks/actions/use-delete-lots"
import { LotSender } from "../../common/hooks/actions/use-send-lots"

type ImportActionsProps = {
  uploader: LotUploader
}

export const StockImportActions = ({ uploader }: ImportActionsProps) => {
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
    <AsyncButton icon={Upload} loading={uploader.loading} onClick={onUpload}>
      Importer lots
    </AsyncButton>
  )
}

export const StockActions = () => (
  <Link relative to="send-complex">
    <Button level="primary" icon={Rapport}>
      Envoi complexe
    </Button>
  </Link>
)

type StockDraftActionsProps = {
  disabled: boolean
  hasSelection: boolean
  uploader: LotUploader
  deleter: LotDeleter
  sender: LotSender
}

export const StockDraftActions = ({
  disabled,
  hasSelection,
  deleter,
  sender,
}: StockDraftActionsProps) => {
  function onValidate() {
    if (hasSelection) {
      sender.sendSelection()
    } else {
      sender.sendAllDrafts()
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
      <AsyncButton
        icon={Check}
        level="success"
        loading={sender.loading}
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
