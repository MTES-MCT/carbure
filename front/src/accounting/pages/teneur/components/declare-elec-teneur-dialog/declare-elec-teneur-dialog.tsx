import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Box, Grid, Main } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { useForm, Form } from "common/components/form2"
import { Button } from "common/components/button2"
import { useElecTeneurDialog } from "./declare-elec-teneur-dialog.hooks"
import { ElecTeneurForm } from "./declare-elec-teneur-dialog.types"
import { NumberInput } from "common/components/inputs2"
import {
  ElecCategoryObjective,
  MainObjective,
  SectorObjective,
  TargetType,
} from "../../types"
import { formatUnit, CONVERSIONS } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"
import {
  Co2TeneurProgressBar,
  EnergyTeneurProgressBar,
} from "../declare-teneur-dialog/declare-teneur-progress-bar"
import { Notice } from "common/components/notice"
import { ObjectiveSectorPicker } from "../objective-sector-picker"
import { useMemo } from "react"
import { formatSector } from "accounting/utils/formatters"
import { formatObjectiveGJ } from "../../utils/objectives"

interface DeclareElecTeneurDialogProps {
  objective: ElecCategoryObjective
  mainObjective?: MainObjective
  sectorObjectives: SectorObjective[]
  onClose: () => void
}

export const DeclareElecTeneurDialog = ({
  objective,
  mainObjective,
  sectorObjectives,
  onClose,
}: DeclareElecTeneurDialogProps) => {
  const { t } = useTranslation()

  const form = useForm<ElecTeneurForm>({})
  const mutation = useElecTeneurDialog({ values: form.value, onClose })

  const avoidedEmissions = ((form.value.quantity ?? 0) * 1000 * 183) / 1e6

  const sectorObjective = useMemo(() => {
    if (!form.value.objective_sector) return undefined

    return sectorObjectives.find(
      (sectorObjective) => sectorObjective.code === form.value.objective_sector
    )
  }, [form.value.objective_sector, sectorObjectives])

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
              <ObjectiveSectorPicker sectorObjectives={sectorObjectives} />
            </Box>

            <Box>
              <NumberInput
                label={t("Quantité déclarée en teneur (GJ)")}
                min={1}
                max={objective.progress.quantity_available}
                {...form.bind("quantity")}
                required
              />

              <Notice noColor variant="info">
                {t("Quantité disponible")}
                {" : "}
                <b>
                  {formatObjectiveGJ(objective.progress.quantity_available)}
                </b>
              </Notice>
            </Box>

            <Box>
              <NumberInput
                label={t("Tonnes de CO2 évitées")}
                value={avoidedEmissions}
                disabled
              />

              <Grid gap="xl">
                {mainObjective && (
                  <Co2TeneurProgressBar
                    teneurDeclared={mainObjective.teneur_declared}
                    pendingTeneur={mainObjective.pending_teneur}
                    target={mainObjective.target}
                    additionalQuantity={avoidedEmissions}
                    label={t("Objectif global")}
                    targetType={TargetType.REACH}
                    formatRemaining={(v) => formatUnit(v, ExtendedUnit.tCO2ev)}
                  />
                )}

                {sectorObjective && (
                  <EnergyTeneurProgressBar
                    objective={sectorObjective}
                    additionalMj={CONVERSIONS.energy.GJ_TO_MJ(
                      form.value.quantity ?? 0
                    )}
                    label={t("Filière {{sector}}", {
                      sector: formatSector(sectorObjective.code),
                    })}
                    targetType={TargetType.REACH}
                  />
                )}
              </Grid>
            </Box>
          </Form>
        </Main>
      </Dialog>
    </Portal>
  )
}
