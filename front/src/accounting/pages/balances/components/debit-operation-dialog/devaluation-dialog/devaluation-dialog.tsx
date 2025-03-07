import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Trans } from "react-i18next"

interface DevaluationDialogProps {
  onClose: () => void
}

export const DevaluationDialog = ({ onClose }: DevaluationDialogProps) => {
  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Réaliser une dévalorisation</Trans>
          </Dialog.Title>
        }
      ></Dialog>
    </Portal>
  )
}
