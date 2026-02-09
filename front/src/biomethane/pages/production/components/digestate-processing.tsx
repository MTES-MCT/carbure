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
  DigestateValorizationMethods,
  SpreadingManagementMethods,
  DigestateSaleTypes,
} from "../types"

import { useSaveProductionUnit } from "../production.hooks"

type DigestateProcessingForm =
  DeepPartial<BiomethaneProductionUnitPatchRequest> & {
    digestate_valorization_methods?: DigestateValorizationMethods[]
    spreading_management_methods?: SpreadingManagementMethods[]
    digestate_sale_types?: DigestateSaleTypes[]
  }

export function DigestateProcessing({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()

  const { bind, value } = useForm<DigestateProcessingForm>({
    has_digestate_phase_separation:
      productionUnit?.has_digestate_phase_separation,
    raw_digestate_treatment_steps:
      productionUnit?.raw_digestate_treatment_steps,
    liquid_phase_treatment_steps: productionUnit?.liquid_phase_treatment_steps,
    solid_phase_treatment_steps: productionUnit?.solid_phase_treatment_steps,
    digestate_valorization_methods:
      productionUnit?.digestate_valorization_methods,
    spreading_management_methods: productionUnit?.spreading_management_methods,
    digestate_sale_types: productionUnit?.digestate_sale_types,
  })

  const { execute: saveProductionUnit, loading } =
    useSaveProductionUnit(productionUnit)

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
      label: t("Incinération / Enfouissement en centre de stockage"),
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
      label: t("Cession gratuite"),
    },
    {
      value: SpreadingManagementMethods.SALE,
      label: t("Vente"),
    },
  ]

  const digestateSaleTypesOptions = [
    {
      value: DigestateSaleTypes.SPREADING_PLAN_ICPE,
      label: t("Plan d'épandage (ICPE)"),
    },
    {
      value: DigestateSaleTypes.AMM,
      label: t("Autorisation de mise sur le marché (AMM)"),
    },
    {
      value: DigestateSaleTypes.MANDATORY_STANDARD,
      label: t("Norme rendue d'application obligatoire"),
    },
    {
      value: DigestateSaleTypes.EU_FERTILIZER_REGULATION,
      label: t("Règlement européen sur les fertilisants"),
    },
    {
      value: DigestateSaleTypes.CDC_DIG,
      label: t("Cahier des Charges CDC Dig"),
    },
  ]

  return (
    <EditableCard title={t("Traitement et valorisation du digestat")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => saveProductionUnit(value!)}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              required
              readOnly={!isEditing}
              label={t("Le digestat subit-il une séparation de phase?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_digestate_phase_separation")}
            />
            {!value.has_digestate_phase_separation && (
              <TextInput
                readOnly={!isEditing}
                label={t(
                  "Étapes complémentaires de traitement du digestat brut"
                )}
                {...bind("raw_digestate_treatment_steps")}
              />
            )}
          </Grid>
          <Grid cols={2} gap="lg">
            {value.has_digestate_phase_separation && (
              <TextInput
                readOnly={!isEditing}
                label={t(
                  "Étape(s) complémentaire(s) de traitement de la phase liquide"
                )}
                {...bind("liquid_phase_treatment_steps")}
              />
            )}
            {value.has_digestate_phase_separation && (
              <TextInput
                readOnly={!isEditing}
                label={t(
                  "Étape(s) complémentaire(s) de traitement de la phase solide"
                )}
                {...bind("solid_phase_treatment_steps")}
              />
            )}
            <CheckboxGroup
              required
              readOnly={!isEditing}
              label={t("Mode de valorisation du digestat")}
              options={digestateValorizationOptions}
              {...bind("digestate_valorization_methods")}
            />
            {value.digestate_valorization_methods?.includes(
              DigestateValorizationMethods.SPREADING
            ) && (
              <>
                <CheckboxGroup
                  required
                  readOnly={!isEditing}
                  label={t("Gestion de l'épandage")}
                  options={spreadingManagementOptions}
                  {...bind("spreading_management_methods")}
                />
                <CheckboxGroup
                  required
                  readOnly={!isEditing}
                  label={t("Sous quel(s) statut(s) est valorisé le digestat")}
                  options={digestateSaleTypesOptions}
                  {...bind("digestate_sale_types")}
                />
              </>
            )}
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
