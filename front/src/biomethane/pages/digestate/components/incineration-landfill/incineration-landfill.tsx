import { Button } from "common/components/button2"
import { TextInput, NumberInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneDigestate,
  BiomethaneDigestateInputRequest,
} from "../../types"
import {
  BiomethaneContract,
  InstallationCategory,
} from "biomethane/pages/contract/types"
import { useSaveDigestate } from "../../digestate.hooks"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration.provider"

type IncinerationLandfillForm = DeepPartial<
  Pick<
    BiomethaneDigestateInputRequest,
    | "annual_eliminated_volume"
    | "incinerator_landfill_center_name"
    | "wwtp_materials_to_incineration"
  >
>

export function IncinerationLandfill({
  digestate,
  contract,
}: {
  digestate?: BiomethaneDigestate
  contract?: BiomethaneContract
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<IncinerationLandfillForm>(
    digestate
      ? {
          annual_eliminated_volume: digestate.annual_eliminated_volume,
          incinerator_landfill_center_name:
            digestate.incinerator_landfill_center_name,
          wwtp_materials_to_incineration:
            digestate.wwtp_materials_to_incineration,
        }
      : {}
  )
  const saveDigestate = useSaveDigestate()
  const isInDeclarationPeriod = useAnnualDeclaration()

  const handleSave = async () => saveDigestate.execute(value)

  return (
    <EditableCard
      title={t("Incinération / Enfouissement")}
      readOnly={!isInDeclarationPeriod}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
          <Grid cols={2} gap="lg">
            <NumberInput
              readOnly={!isEditing}
              label={t("Volume annuel éliminé (t)")}
              type="number"
              {...bind("annual_eliminated_volume")}
              required
            />
            <TextInput
              readOnly={!isEditing}
              label={t(
                "Indiquer le nom de l'incinérateur ou du centre d'enfouissement"
              )}
              {...bind("incinerator_landfill_center_name")}
              required
            />
          </Grid>
          {contract?.installation_category ==
            InstallationCategory.INSTALLATION_CATEGORY_2 && (
            <NumberInput
              readOnly={!isEditing}
              label={t(
                "Quantité de matières totales traitées par la STEP allant en incinération (t)"
              )}
              type="number"
              {...bind("wwtp_materials_to_incineration")}
              required
            />
          )}

          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={saveDigestate.loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
