import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneEnergyInputRequest } from "../types"
import { useSaveEnergy } from "../energy.hooks"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useBiomethaneBackendInputLabel } from "biomethane/hooks/use-biomethane-backend-input-label"

type BiogasProductionForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "produced_biogas_nm3_per_year"
    | "flared_biogas_nm3_per_year"
    | "flaring_operating_hours"
  >
>

const extractValues = (energy?: BiogasProductionForm) => {
  return {
    produced_biogas_nm3_per_year: energy?.produced_biogas_nm3_per_year,
    flared_biogas_nm3_per_year: energy?.flared_biogas_nm3_per_year,
    flaring_operating_hours: energy?.flaring_operating_hours,
  }
}
export function BiogasProduction() {
  const { t } = useTranslation()
  const tBiomethaneInput = useBiomethaneBackendInputLabel()
  const { bind, value } = useFormContext<BiogasProductionForm>()
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveEnergy.execute(extractValues(value))

  return (
    <ManagedEditableCard
      sectionId="biogas-production"
      title={t("Production de biogaz")}
      description={t(
        "Ces informations concernent la production de biogaz (avant épuration)"
      )}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={handleSave}>
          <Grid cols={2} gap="lg">
            <NumberInput
              readOnly={!isEditing}
              label={tBiomethaneInput("energy.produced_biogas_nm3_per_year")}
              type="number"
              min={0}
              {...bind("produced_biogas_nm3_per_year")}
              required
              step={0.01}
            />
            <NumberInput
              readOnly={!isEditing}
              label={tBiomethaneInput("energy.flared_biogas_nm3_per_year")}
              type="number"
              min={0}
              {...bind("flared_biogas_nm3_per_year")}
              required
              step={0.01}
            />
          </Grid>

          <NumberInput
            readOnly={!isEditing}
            label={tBiomethaneInput("energy.flaring_operating_hours")}
            type="number"
            min={0}
            {...bind("flaring_operating_hours")}
            required
          />

          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={saveEnergy.loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
