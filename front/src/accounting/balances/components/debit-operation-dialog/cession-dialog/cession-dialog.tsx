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

interface CessionDialogProps {
  onClose: () => void
  balance: Balance
}

enum CessionStepKey {
  FromDepot = "from_depot",
  Volume = "volume",
  ToDepot = "to_depot",
  Recap = "recap",
}

export const CessionDialog = ({ onClose, balance }: CessionDialogProps) => {
  const { t } = useTranslation()
  const { currentStep, currentStepIndex, steps, nextStep } = useStepper([
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
          </Grid>
          {/* <Notice variant="info" noColor>
            <Trans>Solde disponible</Trans> {balance.biofuel}
            {" : "}
            <b>{formatNumber(Number(balance.available_balance))}l</b>
          </Notice> */}
        </Main>
      </Dialog>
    </Portal>
  )
}
