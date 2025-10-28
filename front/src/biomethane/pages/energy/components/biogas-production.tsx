import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneEnergyInputRequest } from "../types"
import { useSaveEnergy } from "../energy.hooks"
import {
  BiomethaneProductionUnit,
  InstalledMeters,
} from "biomethane/pages/production/types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { EditableCard } from "common/molecules/editable-card"

type BiogasProductionForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "produced_biogas_nm3_per_year"
    | "flared_biogas_nm3_per_year"
    | "flaring_operating_hours"
  >
>

export function BiogasProduction({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<BiogasProductionForm>()
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveEnergy.execute(value)

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
        <EditableCard.Form onSubmit={handleSave}>
          <Grid cols={2} gap="lg">
            <NumberInput
              readOnly={!isEditing}
              label={t("Quantité de biogaz produit (Nm3/an)")}
              type="number"
              {...bind("produced_biogas_nm3_per_year")}
              required
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("Quantité de biogaz torché (Nm3/an)")}
              type="number"
              {...bind("flared_biogas_nm3_per_year")}
              required
            />
          </Grid>
          {productionUnit?.installed_meters?.includes(
            InstalledMeters.FLARING_FLOWMETER
          ) && (
            <NumberInput
              readOnly={!isEditing}
              label={t("Nombre d'heures de fonctionnement de la torchère (h)")}
              type="number"
              {...bind("flaring_operating_hours")}
              required
            />
          )}

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
        </EditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
