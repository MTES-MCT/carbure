import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneDigestateInputRequest } from "../../types"
import { BiomethaneProductionUnit } from "biomethane/pages/production/types"
import { useSaveDigestate } from "../../digestate.hooks"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"

type ProductionForm = DeepPartial<
  Pick<
    BiomethaneDigestateInputRequest,
    | "raw_digestate_tonnage_produced"
    | "raw_digestate_dry_matter_rate"
    | "solid_digestate_tonnage"
    | "liquid_digestate_quantity"
  >
>

const extractValues = (digestate?: ProductionForm) => {
  return {
    raw_digestate_tonnage_produced: digestate?.raw_digestate_tonnage_produced,
    raw_digestate_dry_matter_rate: digestate?.raw_digestate_dry_matter_rate,
    solid_digestate_tonnage: digestate?.solid_digestate_tonnage,
    liquid_digestate_quantity: digestate?.liquid_digestate_quantity,
  }
}
export function Production({
  productionUnit,
}: {
  productionUnit: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<ProductionForm>()
  const saveDigestate = useSaveDigestate()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveDigestate.execute(extractValues(value))

  return (
    <ManagedEditableCard
      sectionId="production"
      title={t("Production de digestat")}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={handleSave}>
          <Grid cols={2} gap="lg">
            {!productionUnit.has_digestate_phase_separation && (
              <>
                <NumberInput
                  readOnly={!isEditing}
                  label={t("Tonnage digestat brut produit (t)")}
                  type="number"
                  {...bind("raw_digestate_tonnage_produced")}
                  required
                />
                <NumberInput
                  readOnly={!isEditing}
                  label={t("Taux de MS du digestat brut (%)")}
                  type="number"
                  min={0}
                  max={100}
                  {...bind("raw_digestate_dry_matter_rate")}
                  required
                />
              </>
            )}
            {productionUnit.has_digestate_phase_separation && (
              <>
                <NumberInput
                  readOnly={!isEditing}
                  label={t("Tonnage de digestat solide (t)")}
                  type="number"
                  {...bind("solid_digestate_tonnage")}
                  required
                />
                <NumberInput
                  readOnly={!isEditing}
                  label={t("Quantité digestat liquide (en m3)")}
                  type="number"
                  {...bind("liquid_digestate_quantity")}
                  required
                />
              </>
            )}
          </Grid>
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
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
