import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"

import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"

import { Check, Return } from "common/components/icons"
import { Box, LoaderOverlay, SystemProps } from "common/components"
import { Button } from "common/components/button"

import styles from "common/components/dialog.module.css"
import { LabelCheckbox } from "common/components/input"
import TransactionSummary, { useSummary } from "./summary"
import { TransactionQuery } from "common/types"

type ValidationPromptProps = SystemProps &
  PromptProps<boolean> & {
    wide?: boolean
    title: string
    description: string
  }

export const ValidationPrompt = ({
  wide = false,
  title,
  description,
  children,
  onResolve,
}: ValidationPromptProps) => {
  const { t } = useTranslation()
  const [checked, setChecked] = useState({ terres: false, infos: false })

  return (
    <Dialog wide={wide} onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

      <Box className={styles.dialogCheckboxes}>
        <LabelCheckbox
          label={t(
            "Je certifie que cette déclaration respecte les critères de durabilité conformément à la réglementation en vigueur."
          )}
          checked={checked.terres}
          onChange={(e) => setChecked({ ...checked, terres: e.target.checked })}
        />
        <LabelCheckbox
          label={t(
            "Je certifie que les informations renseignées sont réelles et valides"
          )}
          checked={checked.infos}
          onChange={(e) => setChecked({ ...checked, infos: e.target.checked })}
        />
      </Box>

      {children}

      <DialogButtons>
        <Button
          disabled={!checked.infos || !checked.terres}
          level="primary"
          icon={Check}
          onClick={() => onResolve(checked.infos && checked.terres)}
        >
          <Trans>Confirmer</Trans>
        </Button>
        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Annuler</Trans>
        </Button>
      </DialogButtons>
    </Dialog>
  )
}

type ValidationSummaryPromptProps = SystemProps &
  PromptProps<number[]> & {
    wide?: boolean
    stock?: boolean
    title: string
    description: string
    query: TransactionQuery
    selection?: number[]
  }

export const ValidationSummaryPrompt = ({
  title,
  description,
  query,
  selection,
  onResolve,
}: ValidationSummaryPromptProps) => {
  const summary = useSummary(query, selection)

  function resolve(isConfirmed?: boolean) {
    if (isConfirmed && summary.data) {
      onResolve(summary.data.tx_ids)
    } else {
      onResolve()
    }
  }

  return (
    <ValidationPrompt
      wide
      title={title}
      description={description}
      onResolve={resolve}
    >
      <TransactionSummary
        in={summary.data?.in ?? null}
        out={summary.data?.out ?? null}
      />
      {summary.loading && <LoaderOverlay />}
    </ValidationPrompt>
  )
}
