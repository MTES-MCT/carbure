import { useState } from "react"

import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"

import { Check } from "common/components/icons"
import { Box, LoaderOverlay } from "common/components"
import { Button } from "common/components/button"

import styles from "common/components/dialog.module.css"
import { LabelCheckbox } from "common/components/input"
import TransactionSummary, { useSummary } from "./summary"
import { TransactionQuery } from "common/types"

type ValidationPromptProps = PromptProps<boolean> & {
  title: string
  description: string
  stock?: boolean
  entityID?: number
  selection?: number[]
  query?: TransactionQuery
}

export const ValidationPrompt = ({
  title,
  description,
  query,
  selection,
  onResolve,
}: ValidationPromptProps) => {
  const summary = useSummary(query, selection)
  const [checked, setChecked] = useState({ terres: false, infos: false })

  return (
    <Dialog
      onResolve={onResolve}
      className={summary.data ? styles.dialogWide : undefined}
    >
      <DialogTitle text={title} />
      <DialogText text={description} />

      <Box className={styles.dialogCheckboxes}>
        <LabelCheckbox
          label="Je certifie que cette déclaration respecte les critères de durabilité liés aux terres"
          checked={checked.terres}
          onChange={(e) => setChecked({ ...checked, terres: e.target.checked })}
        />
        <LabelCheckbox
          label="Je certifie que les informations renseignées sont réelles et valides"
          checked={checked.infos}
          onChange={(e) => setChecked({ ...checked, infos: e.target.checked })}
        />
      </Box>

      {summary.data && (
        <TransactionSummary in={summary.data.in} out={summary.data.out} />
      )}

      <DialogButtons>
        <Button
          disabled={!checked.infos || !checked.terres}
          level="primary"
          icon={Check}
          onClick={() => onResolve(checked.infos && checked.terres)}
        >
          Confirmer
        </Button>
        <Button onClick={() => onResolve()}>Annuler</Button>
      </DialogButtons>

      {summary.loading && <LoaderOverlay />}
    </Dialog>
  )
}
