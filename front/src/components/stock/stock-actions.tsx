import React from "react"

import { Link } from "../relative-route"
import { AsyncButton, Box, Button } from "../system"
import { Rapport, Upload } from "../system/icons"
import { prompt } from "../system/dialog"
import { StockImportPromptFactory } from "../import-prompt"
import { LotUploader } from "../../hooks/actions/use-upload-file"


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