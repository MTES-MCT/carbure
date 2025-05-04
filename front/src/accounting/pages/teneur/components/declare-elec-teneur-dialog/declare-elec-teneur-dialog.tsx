import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Box, Main } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { useForm, Form } from "common/components/form2"
import { Button } from "common/components/button2"
import { useElecTeneurDialog } from "./declare-elec-teneur-dialog.hooks"
import { ElecTeneurForm } from "./declare-elec-teneur-dialog.types"
import { NumberInput } from "common/components/inputs2"
import { ElecCategoryObjective, MainObjective, TargetType } from "../../types"
import { formatNumber, formatUnit } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"
import { DeclareTeneurProgressBar } from "../declare-teneur-dialog/declare-teneur-progress-bar"
import { RecapData } from "../recap-data"
import { Notice } from "common/components/notice"

interface DeclareElecTeneurDialogProps {
  objective: ElecCategoryObjective
  mainObjective?: MainObjective
  onClose: () => void
}

export const DeclareElecTeneurDialog = ({
  objective,
  mainObjective,
  onClose,
}: DeclareElecTeneurDialogProps) => {
  const { t } = useTranslation()

  const form = useForm<ElecTeneurForm>({})
  const mutation = useElecTeneurDialog({ values: form.value, onClose })

  const avoidedEmissions = ((form.value.quantity ?? 0) * 1000 * 183) / 1e6

  let remainingCO2 = 0
  if (mainObjective) {
    remainingCO2 = Math.max(
      0,
      mainObjective.target -
        mainObjective.teneur_declared -
        mainObjective.teneur_declared_month -
        avoidedEmissions
    )
  }

  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Déclarer une teneur</Trans>
          </Dialog.Title>
        }
        footer={
          <Button
            type="submit"
            priority="primary"
            loading={mutation.loading}
            nativeButtonProps={{ form: "elec-teneur-form" }}
          >
            {t("Déclarer la teneur")}
          </Button>
        }
      >
        <Main>
          <Form
            id="elec-teneur-form"
            form={form}
            onSubmit={() => mutation.execute()}
          >
            <Box>
              <NumberInput
                label={t("Quantité déclarée en teneur (GJ)")}
                min={1}
                max={objective.quantity_available}
                {...form.bind("quantity")}
                required
              />

              <Notice noColor variant="info">
                {t("Quantité disponible")}
                {" : "}
                <b>
                  {formatUnit(objective.quantity_available, ExtendedUnit.GJ, {
                    fractionDigits: 0,
                  })}
                </b>
              </Notice>
            </Box>
            <Box>
              <NumberInput
                label={t("Tonnes de CO2 évitées")}
                value={avoidedEmissions}
                disabled
              />

              {mainObjective && (
                <DeclareTeneurProgressBar
                  teneurDeclared={mainObjective.teneur_declared}
                  teneurDeclaredMonth={mainObjective.teneur_declared_month}
                  target={mainObjective.target}
                  quantity={avoidedEmissions}
                  targetType={TargetType.REACH}
                  label={t("Objectif global")}
                />
              )}
              {mainObjective && (
                <RecapData.RemainingQuantityBegoreCO2Objective
                  value={formatNumber(remainingCO2, {
                    fractionDigits: 0,
                    mode: "ceil",
                  })}
                  bold
                  size="md"
                />
              )}
            </Box>
          </Form>
        </Main>
      </Dialog>
    </Portal>
  )
}
