import { Button } from "common/components/button2"
import { NumberInput, RadioGroup } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneEnergyInputRequest } from "../types"
import { useSaveEnergy } from "../energy.hooks"
import { getYesNoOptions } from "common/utils/normalizers"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { EditableCard } from "common/molecules/editable-card"

type AcceptabilityForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "has_opposition_or_complaints_acceptability"
    | "estimated_work_days_acceptability"
  >
>

const extractValues = (energy?: AcceptabilityForm) => {
  return {
    has_opposition_or_complaints_acceptability:
      energy?.has_opposition_or_complaints_acceptability,
    estimated_work_days_acceptability:
      energy?.estimated_work_days_acceptability,
  }
}
export function Acceptability() {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<AcceptabilityForm>()
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveEnergy.execute(extractValues(value))

  return (
    <ManagedEditableCard
      sectionId="acceptability"
      title={t("Acceptabilité")}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t(
                "L'exploitation de votre unité de méthanisation fait-elle l'objet actuellement d'une opposition ou de plaintes de voisinage ?"
              )}
              options={getYesNoOptions()}
              {...bind("has_opposition_or_complaints_acceptability")}
              orientation="horizontal"
              required
            />
            <NumberInput
              readOnly={!isEditing}
              label={t(
                "Nombre de jours de travail estimé pour l'activité de méthanisation sur l'année"
              )}
              {...bind("estimated_work_days_acceptability")}
              required
            />
          </Grid>

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
