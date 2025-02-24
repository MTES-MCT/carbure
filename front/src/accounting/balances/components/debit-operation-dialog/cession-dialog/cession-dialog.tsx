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
import { FromDepotForm } from "./from-depot-form"
import styles from "./cession-dialog.module.css"
import { useForm, Form } from "common/components/form2"
import { CessionStepKey, SessionDialogForm } from "./cession-dialog.types"
import { formatUnit } from "common/utils/formatters"
import { Unit } from "carbure/types"
import { Button } from "common/components/button2"
import { VolumeForm } from "./volume-form"

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
                // disabled={
                //   !form.value.from_depot_available_volume ||
                //   form.value.from_depot_available_volume === 0
                // }
              >
                {t("Précédent")}
              </Button>
            )}
            {nextStep && (
              <Button
                priority="secondary"
                onClick={goToNextStep}
                // disabled={
                //   !form.value.from_depot_available_volume ||
                //   form.value.from_depot_available_volume === 0
                // }
              >
                {t("Suivant")}
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
          <Grid>
            {currentStepIndex > 1 &&
            form.value.from_depot_available_volume &&
            form.value.from_depot_available_volume > 0 ? (
              <>
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
              </>
            ) : null}
          </Grid>

          <div className={styles["cession-dialog__form"]}>
            <Form form={form}>
              {currentStep?.key === CessionStepKey.FromDepot && (
                <FromDepotForm balance={balance} />
              )}
              {currentStep?.key === CessionStepKey.Volume && (
                <VolumeForm balance={balance} />
              )}
            </Form>
          </div>
        </Main>
      </Dialog>
    </Portal>
  )
}
