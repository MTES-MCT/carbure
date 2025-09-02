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
import { useDigestateContext } from "../../digestate.hooks"

type SaleForm = DeepPartial<
  Pick<BiomethaneDigestateInputRequest, "acquiring_companies" | "sold_volume">
>

export function Sale({ digestate }: { digestate?: BiomethaneDigestate }) {
  const { t } = useTranslation()
  const { bind, value } = useForm<SaleForm>(digestate ?? {})
  const { saveDigestate, isInDeclarationPeriod } = useDigestateContext()

  const handleSave = async () => saveDigestate.execute(value)

  return (
    <EditableCard title={t("Vente")} readOnly={!isInDeclarationPeriod}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={handleSave}>
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
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
