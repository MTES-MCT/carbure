import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneDigestate,
  BiomethaneDigestateInputRequest,
} from "../../types"
import { useDigestateContext } from "../../digestate.hooks"

type SpreadingDistanceForm = DeepPartial<
  Pick<
    BiomethaneDigestateInputRequest,
    "average_spreading_valorization_distance"
  >
>

export function SpreadingDistance({
  digestate,
}: {
  digestate?: BiomethaneDigestate
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<SpreadingDistanceForm>(
    digestate
      ? {
          average_spreading_valorization_distance:
            digestate.average_spreading_valorization_distance,
        }
      : {}
  )

  const { saveDigestate, isInDeclarationPeriod } = useDigestateContext()

  const handleSave = async () => saveDigestate.execute(value)

  return (
    <EditableCard
      title={t("Distance d'épandage")}
      description={t("Données par département")}
      readOnly={!isInDeclarationPeriod}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
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
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
