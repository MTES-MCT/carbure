import { Button } from "common/components/button2"
import { CheckboxGroup, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneProductionUnit,
  BiomethaneProductionUnitPatchRequest,
  DigestateSaleType,
} from "../types"
import {
  DigestateValorizationMethodsEnum as DigestateValorizationMethods,
  SpreadingManagementMethodsEnum as SpreadingManagementMethods,
} from "api-schema"
import { useSaveProductionUnit } from "../production.hooks"

type DigestateProcessingForm =
  DeepPartial<BiomethaneProductionUnitPatchRequest> & {
    digestate_valorization_methods?: DigestateValorizationMethods[]
    spreading_management_methods?: SpreadingManagementMethods[]
  }

export function DigestateProcessing({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<DigestateProcessingForm>(productionUnit ?? {})

  const { execute: saveProductionUnit, loading } = useSaveProductionUnit()

  const digestateValorizationOptions = [
    {
      value: DigestateValorizationMethods.SPREADING,
      label: t("Épandage"),
    },
    {
      value: DigestateValorizationMethods.COMPOSTING,
      label: t("Compostage"),
    },
    {
      value: DigestateValorizationMethods.INCINERATION_LANDFILLING,
      label: t("Incinération / Enfouissement"),
    },
  ]

  const spreadingManagementOptions = [
    {
      value: SpreadingManagementMethods.DIRECT_SPREADING,
      label: t("Épandage direct"),
    },
    {
      value: SpreadingManagementMethods.SPREADING_VIA_PROVIDER,
      label: t("Épandage via un prestataire"),
    },
    {
      value: SpreadingManagementMethods.TRANSFER,
      label: t("Cession"),
    },
    {
      value: SpreadingManagementMethods.SALE,
      label: t("Vente"),
    },
  ]

  const digestateSaleTypeOptions = [
    {
      value: DigestateSaleType.DIG_AGRI_SPECIFICATIONS,
      label: t("Cahier de charges DIG Agri"),
    },
    {
      value: DigestateSaleType.HOMOLOGATION,
      label: t("Homologation"),
    },
    {
      value: DigestateSaleType.STANDARDIZED_PRODUCT,
      label: t("Produit normé"),
    },
  ]

  return (
    <EditableCard title={t("Traitement et valorisation du digestat")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => saveProductionUnit(value!)}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t("Le digestat subit-il une séparation de phase?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_digestate_phase_separation")}
            />
            <TextInput
              readOnly={!isEditing}
              label={t("Étapes complémentaires de traitement du digestat brut")}
              {...bind("raw_digestate_treatment_steps")}
              disabled={value.has_digestate_phase_separation}
            />
            <TextInput
              readOnly={!isEditing}
              label={t(
                "Étape(s) complémentaire(s) de traitement de la phase liquide"
              )}
              {...bind("liquid_phase_treatment_steps")}
              disabled={!value.has_digestate_phase_separation}
            />
            <TextInput
              readOnly={!isEditing}
              label={t(
                "Étape(s) complémentaire(s) de traitement de la phase solide"
              )}
              {...bind("solid_phase_treatment_steps")}
              disabled={!value.has_digestate_phase_separation}
            />
            <CheckboxGroup
              readOnly={!isEditing}
              label={t("Mode de valorisation du digestat")}
              options={digestateValorizationOptions}
              {...bind("digestate_valorization_methods")}
            />
            <CheckboxGroup
              readOnly={!isEditing}
              label={t("Gestion de l'épandage")}
              options={spreadingManagementOptions}
              {...bind("spreading_management_methods")}
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("En cas de vente du digestat")}
              options={digestateSaleTypeOptions}
              {...bind("digestate_sale_type")}
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
