import { Button } from "common/components/button2"
import { CheckboxGroup, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"

export function DigestateProcessing() {
  const { t } = useTranslation()

  return (
    <EditableCard title={t("Traitement et valorisation du digestat")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => {}}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t("Le digestat subit-il une séparation de phase?")}
              options={getYesNoOptions()}
              orientation="horizontal"
            />
            <TextInput
              readOnly={!isEditing}
              label={t("Étapes complémentaires de traitement du digestat brut")}
              hintText={t("Que si séparation de phase = Non")}
            />
            <TextInput
              readOnly={!isEditing}
              label={t(
                "Étape(s) complémentaire(s) de traitement de la phase liquide"
              )}
              hintText={t("Que si séparation de phase = Oui, optionnel")}
            />
            <TextInput
              readOnly={!isEditing}
              label={t(
                "Étape(s) complémentaire(s) de traitement de la phase solide"
              )}
              hintText={t("Que si séparation de phase = Oui, optionnel")}
            />
            <CheckboxGroup
              value={[]}
              onChange={() => {}}
              readOnly={!isEditing}
              label={t("Mode de valorisation du digestat")}
              options={[
                {
                  value: "",
                  label: t("Épandage"),
                },
                {
                  value: "",
                  label: t("Compostage"),
                },
                {
                  value: "",
                  label: t("Incinération / Enfouissement"),
                },
              ]}
            />
            <CheckboxGroup
              value={[]}
              onChange={() => {}}
              readOnly={!isEditing}
              label={t("Gestion de l’épandage")}
              options={[
                { value: "", label: t("Épandage direct") },
                { value: "", label: t("Épandage via un prestataire") },
                { value: "", label: t("Cession") },
                { value: "", label: t("Vente") },
              ]}
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("En cas de vente du digestat")}
              options={[
                { value: "", label: t("Cahier de charges DIG Agri") },
                { value: "", label: t("Homologation") },
                { value: "", label: t("Produit normé") },
              ]}
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
