import Dialog from "common/components/dialog2/dialog"
import Portal, { usePortal } from "common/components/portal"
import { Trans } from "react-i18next"
import { RadioGroup } from "common/components/inputs2"
import { useState } from "react"
import styles from "./debit-operation-dialog.module.css"
import { Button } from "common/components/button2"
import { Balance, OperationType } from "accounting/types"
import { formatOperationType } from "accounting/utils/formatters"
import { TransfertDialog } from "./transfert-dialog"

interface DebitOperationDialogProps {
  onClose: () => void
  balance: Balance
}

export const DebitOperationDialog = ({
  onClose,
  balance,
}: DebitOperationDialogProps) => {
  const portal = usePortal()
  const [currentOperation, setCurrentOperation] =
    useState<OperationType.TRANSFERT>(OperationType.TRANSFERT)

  const handleNext = () => {
    switch (currentOperation) {
      case OperationType.TRANSFERT:
        portal((close) => (
          <TransfertDialog
            onClose={close}
            balance={balance}
            onOperationCreated={onClose}
          />
        ))
        break
    }
  }

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
            <Button onClick={handleNext}>
              <Trans>Suivant</Trans>
            </Button>
          </>
        }
      >
        <div className={styles["debit-operation-dialog__radios-container"]}>
          <RadioGroup
            options={[
              {
                label: formatOperationType(OperationType.TRANSFERT),
                value: OperationType.TRANSFERT,
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
