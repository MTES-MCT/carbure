import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Trans } from "react-i18next"

interface ExportationDialogProps {
  onClose: () => void
}

export const ExportationDialog = ({ onClose }: ExportationDialogProps) => {
  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Réaliser une exportation</Trans>
          </Dialog.Title>
        }
      ></Dialog>
    </Portal>
  )
}
