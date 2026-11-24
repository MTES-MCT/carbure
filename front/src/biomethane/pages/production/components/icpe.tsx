import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { BiomethaneProductionUnit, ProductionUnitForm } from "../types"
import { useSaveProductionUnit } from "../production.hooks"
import { useAllowedToEdit } from "biomethane/hooks/use-allowed-to-edit"
import { IcpeNumberField } from "common/molecules/sites/icpe-number-field"
import { IcpeRegimeField } from "common/molecules/sites/icpe-regime-field"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { UnitTypeEnum } from "api-schema"
import { useBiomethaneBackendInputLabel } from "biomethane/hooks/use-biomethane-backend-input-label"

type ICPEForm = Pick<ProductionUnitForm, "icpe_number" | "icpe_regime">

const extractValues = (form?: ICPEForm) => ({
  icpe_number: form?.icpe_number,
  icpe_regime: form?.icpe_regime,
})

export function ICPE({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const tBiomethaneInput = useBiomethaneBackendInputLabel()
  const allowedToEdit = useAllowedToEdit()

  const { bind, value } = useFormContext<ICPEForm>()
  const { execute: saveProductionUnit, loading } =
    useSaveProductionUnit(productionUnit)

  const requiredICPEFields = productionUnit?.unit_type !== UnitTypeEnum.STEP

  return (
    <ManagedEditableCard
      sectionId="icpe"
      title={t("ICPE")}
      readOnly={!allowedToEdit}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form
          onSubmit={() => saveProductionUnit(extractValues(value))}
        >
          <IcpeNumberField
            required={requiredICPEFields}
            readOnly={!isEditing}
            label={tBiomethaneInput("production.icpe_number")}
            state="info"
            {...bind("icpe_number")}
          />
          <IcpeRegimeField
            required={requiredICPEFields}
            readOnly={!isEditing}
            label={tBiomethaneInput("production.icpe_regime")}
            orientation="horizontal"
            hintText={t(
              "Précisez le régime ICPE de l'installation de méthanisation associée à la rubrique 2781 ou 3532"
            )}
            {...bind("icpe_regime")}
          />
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
