import React, { useState } from "react"

import { DialogButtons, PromptFormProps } from "common/components/dialog"

import { Check } from "common/components/icons"
import { Box } from "common/components"
import { Button } from "common/components/button"

import styles from "common/components/dialog.module.css"
import { LabelCheckbox } from "common/components/input"

export const ValidationPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<boolean>) => {
  const [checked, setChecked] = useState({ terres: false, infos: false })

  return (
    <>
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

      <DialogButtons>
        <Button
          disabled={!checked.infos || !checked.terres}
          level="primary"
          icon={Check}
          onClick={() => onConfirm(checked.infos && checked.terres)}
        >
          Envoyer
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </DialogButtons>
    </>
  )
}
