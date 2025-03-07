import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Grid, Main } from "common/components/scaffold"
import { Balance } from "accounting/pages/balances/types"
import { OperationText } from "accounting/components/operation-text"
import { Trans, useTranslation } from "react-i18next"
import { formatSector } from "accounting/utils/formatters"
import { Stepper, useStepper } from "common/components/stepper"
import {
  FromDepotForm,
  FromDepotSummary,
  showNextStepFromDepotForm,
} from "accounting/components/from-depot-form"
import styles from "./cession-dialog.module.css"
import { useForm, Form } from "common/components/form2"
import { CessionStepKey, SessionDialogForm } from "./cession-dialog.types"
import { Button } from "common/components/button2"
import {
  showNextStepQuantityForm,
  QuantityForm,
  QuantitySummary,
} from "accounting/components/quantity-form"
import {
  RecipientToDepotForm,
  RecipientToDepotSummary,
  showNextStepRecipientToDepotForm,
} from "accounting/components/recipient-to-depot-form"
import { simulate, createOperation } from "accounting/api"
import { useMutation } from "common/hooks/async"
import useEntity from "carbure/hooks/entity"
import { CreateOperationType } from "accounting/types"
import { useNotify } from "common/components/notifications"
import { useUnit } from "common/hooks/unit"

interface CessionDialogProps {
  onClose: () => void
  onOperationCreated: () => void
  balance: Balance
}

export const CessionDialog = ({
  onClose,
  onOperationCreated,
  balance,
}: CessionDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const { formatUnit } = useUnit()
  const form = useForm<SessionDialogForm>({})

  const {
    currentStep,
    currentStepIndex,
    steps,
    previousStep,
    nextStep,
    isNextStepAllowed,
    goToNextStep,
    goToPreviousStep,
  } = useStepper(
    [
      {
        key: CessionStepKey.FromDepot,
        title: t("Dépôt d'expédition"),
        allowNextStep: showNextStepFromDepotForm,
      },
      {
        key: CessionStepKey.Quantity,
        title: t("Quantité de la cession et tCO2 évitées"),
        allowNextStep: showNextStepQuantityForm,
      },
      {
        key: CessionStepKey.ToDepot,
        title: t("Redevable et dépôt destinataire"),
        allowNextStep: showNextStepRecipientToDepotForm,
      },
      {
        key: CessionStepKey.Recap,
        title: t("Récapitulatif"),
      },
    ],
    form.value
  )

  const onSubmit = () => {
    return simulate(entity.id, {
      customs_category: balance.customs_category,
      biofuel: balance.biofuel?.id ?? null,
      debited_entity: entity.id,
      target_volume: form.value.quantity!,
      target_emission: form.value.avoided_emissions!,
    }).then((response) => {
      const lots = response.data?.selected_lots
      if (lots) {
        return createOperation(entity.id, {
          lots: lots.map(({ lot_id, ...rest }) => ({
            id: lot_id,
            ...rest,
          })),
          biofuel: balance.biofuel?.id ?? null,
          customs_category: balance.customs_category,
          debited_entity: entity.id,
          type: CreateOperationType.CESSION,
          from_depot: form.value.from_depot?.id,
          to_depot: form.value.to_depot?.id,
          credited_entity: form.value.credited_entity?.id,
        })
      }
    })
  }

  const mutation = useMutation(onSubmit, {
    invalidates: ["balances"],
    onSuccess: () => {
      onClose()
      onOperationCreated()
      notify(
        t(
          "La cession d'une quantité de {{quantity}} a été réalisée avec succès",
          {
            quantity: formatUnit(form.value.quantity!, 0),
          }
        ),
        { variant: "success" }
      )
    },
    onError: () => {
      notify(t("Une erreur est survenue lors de la cession"), {
        variant: "danger",
      })
    },
  })

  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Réaliser une cession</Trans>
          </Dialog.Title>
        }
        footer={
          <>
            {previousStep && (
              <Button
                priority="secondary"
                onClick={goToPreviousStep}
                iconId="ri-arrow-left-s-line"
              >
                {t("Précédent")}
              </Button>
            )}
            {nextStep && (
              <Button
                priority="secondary"
                onClick={goToNextStep}
                disabled={!isNextStepAllowed}
                iconId="ri-arrow-right-s-line"
                iconPosition="right"
              >
                {t("Suivant")}
              </Button>
            )}
            {currentStep?.key === CessionStepKey.Recap && (
              <Button
                priority="primary"
                onClick={() => mutation.execute()}
                loading={mutation.loading}
              >
                {t("Céder")}
              </Button>
            )}
          </>
        }
      >
        <Main>
          <Stepper
            title={currentStep?.title}
            stepCount={steps.length}
            currentStep={currentStepIndex}
            nextTitle={nextStep?.title}
          />
          <Grid>
            <OperationText
              title={t("Filière")}
              description={formatSector(balance.sector)}
            />
            <OperationText
              title={t("Catégorie")}
              description={balance.customs_category ?? ""}
            />
            <OperationText
              title={t("Biocarburant")}
              description={balance.biofuel ? balance.biofuel.code : ""}
            />
            <OperationText
              title={t("Solde disponible en {{biofuel}}", {
                biofuel: balance.biofuel?.code,
              })}
              description={
                balance.available_balance
                  ? formatUnit(balance.available_balance, 0)
                  : ""
              }
            />
          </Grid>
          {currentStepIndex > 1 && <FromDepotSummary values={form.value} />}
          {currentStepIndex > 2 && <QuantitySummary values={form.value} />}
          {currentStepIndex > 3 && form.value.credited_entity && (
            <RecipientToDepotSummary values={form.value} />
          )}
          {currentStep?.key !== CessionStepKey.Recap && (
            <div className={styles["cession-dialog__form"]}>
              <Form form={form}>
                {currentStep?.key === CessionStepKey.FromDepot && (
                  <FromDepotForm balance={balance} />
                )}
                {currentStep?.key === CessionStepKey.Quantity && (
                  <QuantityForm
                    balance={balance}
                    depot_quantity_max={form.value.from_depot?.quantity.credit}
                  />
                )}
                {currentStep?.key === CessionStepKey.ToDepot && (
                  <RecipientToDepotForm />
                )}
              </Form>
            </div>
          )}
        </Main>
      </Dialog>
    </Portal>
  )
}
