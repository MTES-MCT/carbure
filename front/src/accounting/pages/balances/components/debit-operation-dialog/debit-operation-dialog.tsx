import Dialog from "common/components/dialog2/dialog"
import Portal, { usePortal } from "common/components/portal"
import { Trans } from "react-i18next"
import { RadioGroup } from "common/components/inputs2"
import { useState } from "react"
import styles from "./debit-operation-dialog.module.css"
import { Button } from "common/components/button2"
import { CessionDialog } from "./cession-dialog"
import { DevaluationDialog } from "./devaluation-dialog"
import { ExportationDialog } from "./exportation-dialog"
import { Balance, OperationType } from "accounting/types"
import { formatOperationType } from "accounting/utils/formatters"
interface DebitOperationDialogProps {
  onClose: () => void
  balance: Balance
}

export const DebitOperationDialog = ({
  onClose,
  balance,
}: DebitOperationDialogProps) => {
  const portal = usePortal()
  const [currentOperation, setCurrentOperation] = useState<
    | OperationType.CESSION
    | OperationType.DEVALUATION
    | OperationType.EXPORTATION
  >(OperationType.CESSION)

  const handleNext = () => {
    switch (currentOperation) {
      case OperationType.CESSION:
        portal((close) => (
          <CessionDialog
            onClose={close}
            balance={balance}
            onOperationCreated={onClose}
          />
        ))
        break
      case OperationType.DEVALUATION:
        portal((close) => <DevaluationDialog onClose={close} />)
        break
      case OperationType.EXPORTATION:
        portal((close) => (
          <ExportationDialog onClose={close} balance={balance} />
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
