import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Trans } from "react-i18next"
import { Balance } from "../types"
import { RadioGroup } from "common/components/inputs2"
import { OperationType } from "material-accounting/operations/types"
import { useState } from "react"
import { formatOperationType } from "material-accounting/operations/operations.utils"
import styles from "./debit-operation-dialog.module.css"
import { Button } from "common/components/button2"
interface DebitOperationDialogProps {
  onClose: () => void
  balance: Balance
}

export const DebitOperationDialog = ({
  onClose,
}: DebitOperationDialogProps) => {
  const [currentOperation, setCurrentOperation] = useState<
    | OperationType.CESSION
    | OperationType.DEVALUATION
    | OperationType.EXPORTATION
  >(OperationType.CESSION)
  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Réaliser une opération de débit sur mon solde</Trans>
          </Dialog.Title>
        }
        footer={
          <>
            <Button priority="secondary" onClick={onClose}>
              <Trans>Annuler</Trans>
            </Button>
            <Button>
              <Trans>Suivant</Trans>
            </Button>
          </>
        }
      >
        <div className={styles["debit-operation-dialog__radios-container"]}>
          <RadioGroup
            options={[
              {
                label: formatOperationType(OperationType.CESSION),
                hintText: "Additional information",
                value: OperationType.CESSION,
              },
              {
                label: formatOperationType(OperationType.DEVALUATION),
                hintText: "Additional information",
                value: OperationType.DEVALUATION,
              },
              {
                label: formatOperationType(OperationType.EXPORTATION),
                hintText: "Additional information",
                value: OperationType.EXPORTATION,
              },
            ]}
            onChange={setCurrentOperation}
            value={currentOperation}
            className={styles["debit-operation-dialog__radios"]}
          />
        </div>
      </Dialog>
    </Portal>
  )
}
