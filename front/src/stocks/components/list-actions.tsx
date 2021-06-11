import React, { Fragment } from "react"
import { Trans, useTranslation } from "react-i18next"

import { Link } from "common/components/relative-route"
import {
  Check,
  Cross,
  Flask,
  Rapport,
  Upload,
  Forward,
} from "common/components/icons"
import { AsyncButton, Button } from "common/components/button"
import { prompt } from "common/components/dialog"
import { StockImportPrompt } from "transactions/components/import"
import { LotUploader } from "transactions/hooks/actions/use-upload-file"
import { LotDeleter } from "transactions/hooks/actions/use-delete-lots"
import { LotSender } from "stocks/hooks/use-send-lots"

type ImportActionsProps = {
  uploader: LotUploader
}

export const StockImportActions = ({ uploader }: ImportActionsProps) => {
  async function onUpload() {
    const file = await prompt<File>((resolve) => (
      <StockImportPrompt uploader={uploader} onResolve={resolve} />
    ))

    if (file) {
      uploader.uploadMassBalanceFile(file)
    }
  }

  return (
    <AsyncButton icon={Upload} loading={uploader.loading} onClick={onUpload}>
      <Trans>Importer lots</Trans>
    </AsyncButton>
  )
}

type StockActionsProps = {
  onForward: () => void
  onConvertETBE: () => void
}

export const StockActions = ({
  onForward,
  onConvertETBE,
}: StockActionsProps) => (
  <Fragment>
    <Link relative to="send-complex">
      <Button level="primary" icon={Rapport}>
        <Trans>Envoi complexe</Trans>
      </Button>
    </Link>

    <Button level="primary" icon={Forward} onClick={onForward}>
      <Trans>Transférer</Trans>
    </Button>

    <Button level="primary" icon={Flask} onClick={onConvertETBE}>
      <Trans>Convertir ETBE</Trans>
    </Button>
  </Fragment>
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
  const { t } = useTranslation()

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
      deleter.deleteAll()
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
        <Trans>
          Envoyer {{ what: hasSelection ? t("sélection") : t("tout") }}
        </Trans>
      </AsyncButton>

      <AsyncButton
        icon={Cross}
        level="danger"
        loading={deleter.loading}
        disabled={disabled}
        onClick={onDelete}
      >
        <Trans>
          Supprimer {{ what: hasSelection ? t("sélection") : t("tout") }}
        </Trans>
      </AsyncButton>
    </React.Fragment>
  )
}
