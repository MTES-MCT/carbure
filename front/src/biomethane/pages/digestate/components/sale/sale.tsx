import { Button } from "common/components/button2"
import { TextInput, NumberInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneDigestateInputRequest } from "../../types"
import { useSaveDigestate } from "../../digestate.hooks"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

type SaleForm = DeepPartial<
  Pick<BiomethaneDigestateInputRequest, "acquiring_companies" | "sold_volume">
>

const extractValues = (digestate?: SaleForm) => {
  return {
    acquiring_companies: digestate?.acquiring_companies,
    sold_volume: digestate?.sold_volume,
  }
}

export function Sale() {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<SaleForm>()
  const saveDigestate = useSaveDigestate()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSave = async () => saveDigestate.execute(extractValues(value))

  return (
    <ManagedEditableCard
      sectionId="sale"
      title={t("Vente")}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={handleSave}>
          <Grid cols={2} gap="lg">
            <TextInput
              readOnly={!isEditing}
              label={t("Entreprise(s) acquérant le digestat")}
              hintText={t("Si plusieurs éléments, séparez par des virgules")}
              {...bind("acquiring_companies")}
              required
            />
            <NumberInput
              readOnly={!isEditing}
              label={t("Volume vendu (t)")}
              type="number"
              {...bind("sold_volume")}
              required
            />
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
