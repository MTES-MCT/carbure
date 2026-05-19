import { Button } from "common/components/button2"
import { CheckboxGroup, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import {
  BiomethaneProductionUnit,
  ProductionUnitForm,
  DigestateValorizationMethods,
  SpreadingManagementMethods,
  DigestateSaleTypes,
} from "../types"
import { useSaveProductionUnit } from "../production.hooks"
import { useAllowedToEdit } from "biomethane/hooks/use-allowed-to-edit"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useBiomethaneBackendInputLabel } from "biomethane/hooks/use-biomethane-backend-input-label"

type DigestateProcessingForm = Pick<
  ProductionUnitForm,
  | "has_digestate_phase_separation"
  | "raw_digestate_treatment_steps"
  | "liquid_phase_treatment_steps"
  | "solid_phase_treatment_steps"
> & {
  digestate_valorization_methods?: DigestateValorizationMethods[]
  spreading_management_methods?: SpreadingManagementMethods[]
  digestate_sale_types?: DigestateSaleTypes[]
}

const extractValues = (form?: DigestateProcessingForm) => ({
  has_digestate_phase_separation: form?.has_digestate_phase_separation,
  raw_digestate_treatment_steps: form?.raw_digestate_treatment_steps,
  liquid_phase_treatment_steps: form?.liquid_phase_treatment_steps,
  solid_phase_treatment_steps: form?.solid_phase_treatment_steps,
  digestate_valorization_methods: form?.digestate_valorization_methods,
  spreading_management_methods: form?.spreading_management_methods,
  digestate_sale_types: form?.digestate_sale_types,
})

export function DigestateProcessing({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const tBiomethaneInput = useBiomethaneBackendInputLabel()
  const allowedToEdit = useAllowedToEdit()

  const { bind, value } = useFormContext<DigestateProcessingForm>()
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
    <ManagedEditableCard
      sectionId="digestate-processing"
      title={t("Traitement et valorisation du digestat")}
      readOnly={!allowedToEdit}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form
          onSubmit={() => saveProductionUnit(extractValues(value))}
        >
          <Grid cols={2} gap="lg">
            <RadioGroup
              required
              readOnly={!isEditing}
              label={tBiomethaneInput(
                "production.has_digestate_phase_separation"
              )}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_digestate_phase_separation")}
            />
            {!value.has_digestate_phase_separation && (
              <TextInput
                readOnly={!isEditing}
                label={tBiomethaneInput(
                  "production.raw_digestate_treatment_steps"
                )}
                {...bind("raw_digestate_treatment_steps")}
              />
            )}
          </Grid>
          <Grid cols={2} gap="lg">
            {value.has_digestate_phase_separation && (
              <TextInput
                readOnly={!isEditing}
                label={tBiomethaneInput(
                  "production.liquid_phase_treatment_steps"
                )}
                {...bind("liquid_phase_treatment_steps")}
              />
            )}
            {value.has_digestate_phase_separation && (
              <TextInput
                readOnly={!isEditing}
                label={tBiomethaneInput(
                  "production.solid_phase_treatment_steps"
                )}
                {...bind("solid_phase_treatment_steps")}
              />
            )}
            <CheckboxGroup
              required
              readOnly={!isEditing}
              label={tBiomethaneInput(
                "production.digestate_valorization_methods"
              )}
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
                  label={tBiomethaneInput(
                    "production.spreading_management_methods"
                  )}
                  options={spreadingManagementOptions}
                  {...bind("spreading_management_methods")}
                />
                <CheckboxGroup
                  required
                  readOnly={!isEditing}
                  label={tBiomethaneInput("production.digestate_sale_types")}
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
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
