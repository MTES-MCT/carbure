import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"

export function GeneralInfo() {
  const { t } = useTranslation()

  return (
    <EditableCard title={t("Informations générales du site de production")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => {}}>
          <Grid cols={2} gap="lg">
            <TextInput
              readOnly={!isEditing}
              label={t("Nom de l’unité")}
              //
            />
            <TextInput
              readOnly={!isEditing}
              label={t("SIRET")}
              //
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Type d’installation")}
              options={[
                { value: "", label: t("Agricole autonome") },
                { value: "", label: t("Agricole territorial") },
                { value: "", label: t("Industriel territorial") },
                { value: "", label: t("Déchets ménagers et biodéchets") },
                { value: "", label: t("ISDND") },
              ]}
            />
            <TextInput
              readOnly={!isEditing}
              label={t("Adresse de la société (Numéro et rue)")}
              //
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
