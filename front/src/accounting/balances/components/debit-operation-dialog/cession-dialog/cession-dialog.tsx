import Dialog from "common/components/dialog2/dialog"
// import { Notice } from "common/components/notice"
import Portal from "common/components/portal"
import { Grid, Main } from "common/components/scaffold"
// import { formatNumber } from "common/utils/formatters"
import { Balance } from "accounting/balances/types"
import { OperationText } from "accounting/components/operation-text"
import { Trans, useTranslation } from "react-i18next"
import { formatSector } from "accounting/utils/formatters"
import { Stepper, useStepper } from "common/components/stepper"
import { FromDepotForm, showNextStepFromDepotForm } from "./from-depot-form"
import styles from "./cession-dialog.module.css"
import { useForm, Form } from "common/components/form2"
import { CessionStepKey, SessionDialogForm } from "./cession-dialog.types"
import { formatUnit } from "common/utils/formatters"
import { Unit } from "carbure/types"
import { Button } from "common/components/button2"
import { showNextStepVolumeForm, VolumeForm } from "./volume-form"
import { useMemo } from "react"
import {
  RecipientToDepotForm,
  showNextStepRecipientToDepotForm,
} from "./recipient-to-depot-form"

interface CessionDialogProps {
  onClose: () => void
  balance: Balance
}

export const CessionDialog = ({ onClose, balance }: CessionDialogProps) => {
  const { t } = useTranslation()
  const {
    currentStep,
    currentStepIndex,
    steps,
    previousStep,
    nextStep,
    goToNextStep,
    goToPreviousStep,
  } = useStepper([
    {
      key: CessionStepKey.FromDepot,
      title: t("Dépôt d'expédition"),
    },
    {
      key: CessionStepKey.Volume,
      title: t("Volume de la cession en litres et tCO2 évitées"),
    },
    {
      key: CessionStepKey.ToDepot,
      title: t("Redevable et dépôt destinataire"),
    },
    {
      key: CessionStepKey.Recap,
      title: t("Récapitulatif"),
    },
  ])
  const form = useForm<SessionDialogForm>({})

  const showNextStep = useMemo(() => {
    if (currentStep?.key === CessionStepKey.FromDepot) {
      return showNextStepFromDepotForm(form.value)
    }
    if (currentStep?.key === CessionStepKey.Volume) {
      return showNextStepVolumeForm(form.value)
    }
    if (currentStep?.key === CessionStepKey.ToDepot) {
      return showNextStepRecipientToDepotForm(form.value)
    }
    return true
  }, [currentStep, form.value])

  const createOperation = () => {
    console.log(form.value)
  }

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
                disabled={!showNextStep}
                iconId="ri-arrow-right-s-line"
                iconPosition="right"
              >
                {t("Suivant")}
              </Button>
            )}
            {currentStep?.key === CessionStepKey.Recap && (
              <Button priority="primary" onClick={createOperation}>
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
              description={balance.biofuel ?? ""}
            />
            <OperationText
              title={t("Solde disponible")}
              description={
                balance.available_balance
                  ? formatUnit(balance.available_balance, Unit.l, 0)
                  : ""
              }
            />
          </Grid>
          {currentStepIndex > 1 &&
          form.value.from_depot_available_volume &&
          form.value.from_depot_available_volume > 0 ? (
            <Grid>
              <OperationText
                title={t("Dépôt d'expédition")}
                description={form.value.from_depot?.name ?? ""}
              />
              <OperationText
                title={t("Solde disponible dans le dépôt d'expédition")}
                description={formatUnit(
                  form.value.from_depot_available_volume,
                  Unit.l,
                  0
                )}
              />
            </Grid>
          ) : null}
          {currentStepIndex > 2 &&
          form.value.volume &&
          form.value.avoided_emissions ? (
            <Grid>
              <OperationText
                title={t("Quantité de la cession")}
                description={formatUnit(form.value.volume, Unit.l, 0)}
              />
              <OperationText
                title={t("TCO2 évitées équivalentes")}
                description={form.value.avoided_emissions}
              />
            </Grid>
          ) : null}
          {currentStepIndex > 3 && form.value.credited_entity && (
            <Grid>
              <OperationText
                title={t("Redevable")}
                description={form.value.credited_entity.name}
              />
              {form.value.to_depot && (
                <OperationText
                  title={t("Dépôt destinataire")}
                  description={form.value.to_depot?.name ?? ""}
                />
              )}
            </Grid>
          )}
          {currentStep?.key !== CessionStepKey.Recap && (
            <div className={styles["cession-dialog__form"]}>
              <Form form={form}>
                {currentStep?.key === CessionStepKey.FromDepot && (
                  <FromDepotForm balance={balance} />
                )}
                {currentStep?.key === CessionStepKey.Volume && (
                  <VolumeForm balance={balance} />
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
