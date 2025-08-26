import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneDigestate,
  BiomethaneDigestatePatchRequest,
} from "../../types"
import { useDigestateContext } from "../../digestate.hooks"

type InjectionSiteForm = DeepPartial<
  Pick<
    BiomethaneDigestatePatchRequest,
    | "raw_digestate_tonnage_produced"
    | "raw_digestate_dry_matter_rate"
    | "solid_digestate_tonnage"
    | "liquid_digestate_quantity"
  >
>

export function InjectionSite({
  digestate,
}: {
  digestate?: BiomethaneDigestate
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<InjectionSiteForm>(digestate ?? {})
  const { saveDigestate } = useDigestateContext()

  const handleSave = async () => saveDigestate(value)

  return (
    <EditableCard title={t("Site d'injection")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
          <Grid cols={2} gap="lg">
            <NumberInput
              readOnly={!isEditing}
              label={t("Tonnage digestat brut produit (t)")}
              type="number"
              {...bind("raw_digestate_tonnage_produced")}
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("Taux de MS du digestat brut (%)")}
              type="number"
              min={0}
              max={100}
              {...bind("raw_digestate_dry_matter_rate")}
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("Tonnage de digestat solide (t)")}
              type="number"
              {...bind("solid_digestate_tonnage")}
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("Quantité digestat liquide (en m3)")}
              type="number"
              {...bind("liquid_digestate_quantity")}
            />
          </Grid>
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
