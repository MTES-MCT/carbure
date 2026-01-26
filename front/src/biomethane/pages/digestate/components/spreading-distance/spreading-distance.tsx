import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneDigestateInputRequest } from "../../types"
import { useSaveDigestate } from "../../digestate.hooks"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

type SpreadingDistanceForm = DeepPartial<
  Pick<
    BiomethaneDigestateInputRequest,
    "average_spreading_valorization_distance"
  >
>

const extractValues = (digestate?: SpreadingDistanceForm) => {
  return {
    average_spreading_valorization_distance:
      digestate?.average_spreading_valorization_distance,
  }
}
export function SpreadingDistance() {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<SpreadingDistanceForm>()

  const saveDigestate = useSaveDigestate()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveDigestate.execute(extractValues(value))

  return (
    <ManagedEditableCard
      sectionId="spreading-distance"
      title={t("Distance d'épandage")}
      description={t("Donnée du plan d'épandage mis en oeuvre")}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={handleSave}>
          <NumberInput
            readOnly={!isEditing}
            label={t("Distance moyenne de valorisation d'épandage (km)")}
            {...bind("average_spreading_valorization_distance")}
            required
          />
          {isEditing && (
            <Button type="submit" iconId="ri-save-line" asideX>
              {t("Sauvegarder")}
            </Button>
          )}
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
