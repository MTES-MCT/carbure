import { showNextStepAdvancedFilters } from "accounting/components/advanced-filters/advanced-filters.utils"
import { useQuantityFormStep } from "accounting/components/quantity-form"
import { DebtType } from "accounting/types"
import { formatAccountingUnit } from "accounting/utils/formatters"
import { getDebtRepaymentType } from "accounting/utils/debts"
import { useForm } from "common/components/form2"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { RadioGroup } from "common/components/inputs2"
import { Box, Main } from "common/components/scaffold"
import { StepperProvider } from "common/components/stepper"
import { Unit } from "common/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useDebtRepaymentSimulation } from "./debt-repayment-dialog.hooks"
import {
  DEBT_REPAYMENT_FILTERS_STEP_KEY,
  DebtRepaymentDialogContent,
  DEBT_REPAYMENT_TCO2_STEP_KEY,
} from "./debt-repayment-dialog-content"
import {
  DebtRepaymentDialogContentProps,
  DebtRepaymentDialogForm,
  DebtRepaymentDialogProps,
} from "./debt-repayment-dialog.types"
import { formatDebtTco2 } from "./debt-repayment-dialog-notices"

export { DebtRepaymentDialogContent }
export { DebtRepaymentTco2Summary } from "./debt-repayment-dialog-notices"

const DebtRepaymentSteps = ({
  debtType,
  ...props
}: DebtRepaymentDialogProps &
  Pick<DebtRepaymentDialogContentProps, "debtType">) => {
  const { t } = useTranslation()
  const form = useForm<DebtRepaymentDialogForm>({})
  const simulation = useDebtRepaymentSimulation(props.balance, form)
  const quantityStep = useQuantityFormStep({
    balance: props.balance,
    form,
    overrides: {
      title: t(
        "Quantité d'énergie acquittée et tonnes de CO2 évitées équivalentes"
      ),
    },
  })

  const steps = [
    {
      key: DEBT_REPAYMENT_FILTERS_STEP_KEY,
      title: t("Filtres"),
      allowNextStep:
        debtType === DebtType.TCO2
          ? (form.value.availableBalance ?? 0) > 0
          : showNextStepAdvancedFilters(form.value),
      onSubmit: debtType === DebtType.TCO2 ? simulation.execute : undefined,
    },
    debtType === DebtType.TCO2
      ? {
          key: DEBT_REPAYMENT_TCO2_STEP_KEY,
          title: t("Volume prélevé et dette en tCO2 évitées acquittée"),
          allowNextStep: (form.value.simulation?.repaid_tco2 ?? 0) > 0,
        }
      : quantityStep,
    { key: "recap", title: t("Récapitulatif") },
  ]

  return (
    <StepperProvider steps={steps}>
      <DebtRepaymentDialogContent {...props} form={form} debtType={debtType} />
    </StepperProvider>
  )
}

export const DebtRepaymentDialog = (props: DebtRepaymentDialogProps) => {
  const { t } = useTranslation()
  const [selectedDebtType, setDebtType] = useState<DebtType>()
  const [choice, setChoice] = useState<DebtType>(DebtType.VOLUME)
  const debtType = getDebtRepaymentType(props.debt, selectedDebtType)

  if (!debtType) {
    return (
      <Dialog
        fullWidth
        onClose={props.onClose}
        header={<Dialog.Title>{t("Acquittement de dette")}</Dialog.Title>}
        footer={
          <>
            <Button priority="secondary" onClick={props.onClose}>
              {t("Annuler")}
            </Button>
            <Button onClick={() => setDebtType(choice)}>{t("Suivant")}</Button>
          </>
        }
      >
        <Main>
          <p>{t("Choisissez la dette à acquitter :")}</p>
          <Box>
            <RadioGroup
              value={choice}
              onChange={setChoice}
              options={[
                {
                  value: DebtType.VOLUME,
                  label: t("Dette de volume : {{volume}}", {
                    volume: formatAccountingUnit(
                      props.debt.remaining_volume,
                      Unit.l
                    ),
                  }),
                },
                {
                  value: DebtType.TCO2,
                  label: t("Dette en émissions évitées : {{amount}}", {
                    amount: formatDebtTco2(props.debt.remaining_tco2),
                  }),
                },
              ]}
            />
          </Box>
        </Main>
      </Dialog>
    )
  }

  return <DebtRepaymentSteps {...props} key={debtType} debtType={debtType} />
}
