import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneProductionUnit,
  BiomethaneProductionUnitAddRequest,
} from "biomethane/types"
import {
  useMutateProductionUnit,
  useUnitTypeOptions,
} from "../../production.hooks"

type GeneralInfoForm = DeepPartial<BiomethaneProductionUnitAddRequest>

export function GeneralInfo({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<GeneralInfoForm>(productionUnit ?? {})
  const unitTypeOptions = useUnitTypeOptions()
  const { execute: updateProductionUnit, loading } = useMutateProductionUnit(
    productionUnit !== undefined
  )

  return (
    <EditableCard title={t("Informations générales du site de production")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => updateProductionUnit(value!)}>
          <Grid cols={2} gap="lg">
            <TextInput
              readOnly={!isEditing}
              label={t("Nom de l'unité")}
              required
              {...bind("unit_name")}
            />
            <TextInput
              readOnly={!isEditing}
              label={t("SIRET")}
              required
              {...bind("siret_number")}
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Type d'installation")}
              options={unitTypeOptions}
              required
              {...bind("unit_type")}
            />
            <TextInput
              readOnly={!isEditing}
              label={t("Adresse de la société (Numéro et rue)")}
              required
              {...bind("company_address")}
            />
          </Grid>
          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
