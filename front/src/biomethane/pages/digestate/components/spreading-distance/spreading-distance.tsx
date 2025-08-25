import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneDigestate,
  BiomethaneDigestatePatchRequest,
} from "../../types"

type SpreadingDistanceForm = DeepPartial<
  Pick<
    BiomethaneDigestatePatchRequest,
    "average_spreading_valorization_distance"
  >
>

export function SpreadingDistance({
  digestate,
}: {
  digestate?: BiomethaneDigestate
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<SpreadingDistanceForm>(digestate ?? {})

  const handleSave = async () => {
    // TODO: Implémenter la sauvegarde
    console.log("Sauvegarde des données de distance d'épandage:", value)
  }

  return (
    <EditableCard
      title={t("Distance d'épandage")}
      description={t(
        "Données par département, Que si Épandage déclaré (dans paramètres)"
      )}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
          <NumberInput
            readOnly={!isEditing}
            label={t("Distance moyenne de valorisation d'épandage (km)")}
            {...bind("average_spreading_valorization_distance")}
          />
          {isEditing && (
            <Button type="submit" iconId="ri-save-line" asideX>
              {t("Sauvegarder")}
            </Button>
          )}
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
