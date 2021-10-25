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
import { Box, SystemProps } from "common/components"
import { Button } from "common/components/button"

import styles from "common/components/dialog.module.css"
import { LabelCheckbox, LabelInput } from "common/components/input"

export interface PinConfig {
  checked: boolean
  comment: string
}

type PinPromptProps = SystemProps &
  PromptProps<PinConfig> & {
    title: string
    description: string
    role: "admin" | "auditor"
  }

export const PinPrompt = ({
  title,
  description,
  children,
  role,
  onResolve,
}: PinPromptProps) => {
  const { t } = useTranslation()
  const [checked, setChecked] = useState(false)
  const [comment, setComment] = useState("")

  const label =
    role === "admin"
      ? t("Partager ce commentaire avec les auditeurs")
      : t("Partager ce commentaire avec l'administration")

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

      <Box>
        <LabelInput
          label={t("Commentaire")}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
      </Box>

      <Box className={styles.dialogCheckboxes}>
        <LabelCheckbox
          label={label}
          checked={checked}
          onChange={(e) => setChecked(e.target.checked)}
        />
      </Box>

      {children}

      <DialogButtons>
        <Button
          level="primary"
          icon={Check}
          onClick={() => onResolve({ checked, comment })}
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
