import Dialog from "common/components/dialog2/dialog"
import Portal, { usePortal } from "common/components/portal"
import { Trans } from "react-i18next"
import { RadioGroup } from "common/components/inputs2"
//import { LoaderOverlay } from "common/components/scaffold"
import { useState } from "react"
import styles from "./debit-operation-dialog.module.css"
import { Button } from "common/components/button2"
import { CessionDialog } from "./cession-dialog"
import { Balance, OperationType } from "accounting/types"
import { formatOperationType } from "accounting/utils/formatters"
import { TransfertDialog } from "./transfert-dialog"
//import { getObjectives } from "accounting/pages/teneur/api"
//import { useQuery } from "common/hooks/async"
//import useEntity from "common/hooks/entity"

interface DebitOperationDialogProps {
  onClose: () => void
  balance: Balance
}

export const DebitOperationDialog = ({
  onClose,
  balance,
}: DebitOperationDialogProps) => {
  //const entity = useEntity()
  const portal = usePortal()
  const [currentOperation, setCurrentOperation] = useState<
    | OperationType.CESSION
    | OperationType.DEVALUATION
    | OperationType.EXPORTATION
    | OperationType.TRANSFERT
  >(OperationType.CESSION)

  //const { result, loading } = useQuery(getObjectives, {
  //  key: "teneur-objectives",
  //  params: [entity.id, 2025, false],
  //})

  // const objectivesData = result

  //if (loading) {
  //  return <LoaderOverlay />
  //}

  /*const displayTransfert = () => {
    if (objectivesData) {
      const category = balance.customs_category
      const categoryObjective =
        objectivesData?.objectivized_categories.find(
          (cat) => cat.code === category
        ) ||
        objectivesData?.capped_categories.find((cat) => cat.code === category)

      return (
        categoryObjective &&
        categoryObjective.target <= categoryObjective.teneur_declared
      )
    }
    return false
  }*/

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
              //{
              //  label: formatOperationType(OperationType.CESSION),
              //  value: OperationType.CESSION,
              //},
              //...(displayTransfert()
              //  ? [
              {
                label: formatOperationType(OperationType.TRANSFERT),
                value: OperationType.TRANSFERT,
              },
              //   ]
              // : []),
              // {
              //   label: formatOperationType(OperationType.DEVALUATION),
              //   hintText: "Additional information",
              //   value: OperationType.DEVALUATION,
              // },
              // {
              //   label: formatOperationType(OperationType.EXPORTATION),
              //   value: OperationType.EXPORTATION,
              // },
            ]}
            onChange={(value) => {
              if (
                value === OperationType.CESSION ||
                value === OperationType.DEVALUATION ||
                value === OperationType.EXPORTATION ||
                value === OperationType.TRANSFERT
              ) {
                setCurrentOperation(value)
              }
            }}
            value={currentOperation}
            className={styles["debit-operation-dialog__radios"]}
          />
        </div>
      </Dialog>
    </Portal>
  )
}
