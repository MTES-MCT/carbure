import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneDigestate,
  BiomethaneDigestateInputRequest,
} from "../../types"
import { useDigestateContext } from "../../digestate.hooks"
import { BiomethaneProductionUnit } from "biomethane/pages/production/types"

type ProductionForm = DeepPartial<
  Pick<
    BiomethaneDigestateInputRequest,
    | "raw_digestate_tonnage_produced"
    | "raw_digestate_dry_matter_rate"
    | "solid_digestate_tonnage"
    | "liquid_digestate_quantity"
  >
>

export function Production({
  digestate,
  productionUnit,
}: {
  digestate?: BiomethaneDigestate
  productionUnit: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<ProductionForm>(
    digestate
      ? {
          raw_digestate_tonnage_produced:
            digestate.raw_digestate_tonnage_produced,
          raw_digestate_dry_matter_rate:
            digestate.raw_digestate_dry_matter_rate,
          solid_digestate_tonnage: digestate.solid_digestate_tonnage,
          liquid_digestate_quantity: digestate.liquid_digestate_quantity,
        }
      : {}
  )
  const { saveDigestate, isInDeclarationPeriod } = useDigestateContext()

  const handleSave = async () => saveDigestate.execute(value)

  return (
    <EditableCard
      title={t("Production de digestat")}
      readOnly={!isInDeclarationPeriod}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
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
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
