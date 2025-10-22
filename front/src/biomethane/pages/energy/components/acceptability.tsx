import { Button } from "common/components/button2"
import { NumberInput, RadioGroup } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneEnergy, BiomethaneEnergyInputRequest } from "../types"
import { useSaveEnergy } from "../energy.hooks"
import { getYesNoOptions } from "common/utils/normalizers"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration.provider"

type AcceptabilityForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "has_opposition_or_complaints_acceptability"
    | "estimated_work_days_acceptability"
  >
>

export function Acceptability({ energy }: { energy?: BiomethaneEnergy }) {
  const { t } = useTranslation()
  const { bind, value } = useForm<AcceptabilityForm>(energy ?? {})
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveEnergy.execute(value)

  return (
    <EditableCard title={t("Acceptabilité")} readOnly={!canEditDeclaration}>
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
    </EditableCard>
  )
}
