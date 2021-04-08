import { useEffect, useState } from "react"

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
import TransactionSummary from "./transaction-summary"
import useAPI from "common/hooks/use-api"
import * as api from "../api"

type ValidationPromptProps = PromptProps<boolean> & {
  title: string
  description: string
  stock?: boolean
  entityID?: number
  selection?: number[]
}

export const ValidationPrompt = ({
  title,
  description,
  stock,
  entityID,
  selection,
  onResolve,
}: ValidationPromptProps) => {
  const [checked, setChecked] = useState({ terres: false, infos: false })
  const [draftSummary, getDraftSummary] = useAPI(api.getDraftSummary)

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      getDraftSummary(entityID, selection, stock)
    }
  }, [getDraftSummary, entityID, selection])

  return (
    <Dialog
      onResolve={onResolve}
      className={draftSummary.data ? styles.dialogWide : undefined}
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

      {draftSummary.data && (
        <TransactionSummary
          in={draftSummary.data.in}
          out={draftSummary.data.out}
        />
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

      {draftSummary.loading && <LoaderOverlay />}
    </Dialog>
  )
}
