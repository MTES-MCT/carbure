import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"

export function SanitaryAgreement() {
  const { t } = useTranslation()

  return (
    <EditableCard title={t("Agrément sanitaire")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => {}}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t("Votre site dispose-t-il d’un agrément sanitaire ?")}
              options={getYesNoOptions()}
              orientation="horizontal"
            />
            <TextInput
              readOnly={!isEditing}
              label={t("N° Agrément sanitaire")}
              placeholder="FR XX-XX-XXX"
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Disposez vous d’une dérogation à l’hygiénisation?")}
              options={getYesNoOptions()}
              orientation="horizontal"
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Si oui, dérogation à l’hygiénisation :")}
              options={getYesNoOptions()}
              orientation="horizontal"
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
