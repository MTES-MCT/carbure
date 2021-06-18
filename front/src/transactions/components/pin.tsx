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
import { LabelCheckbox } from "common/components/input"

type PinPromptProps = SystemProps &
  PromptProps<boolean> & {
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

  const label =
    role === "admin"
      ? t("Signaler ces lots aux auditeurs")
      : t("Signaler ces lots à l'administration")

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

      <Box className={styles.dialogCheckboxes}>
        <LabelCheckbox
          label={label}
          checked={checked}
          onChange={(e) => setChecked(e.target.checked)}
        />
      </Box>

      {children}

      <DialogButtons>
        <Button level="primary" icon={Check} onClick={() => onResolve(checked)}>
          <Trans>Confirmer</Trans>
        </Button>
        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Annuler</Trans>
        </Button>
      </DialogButtons>
    </Dialog>
  )
}
