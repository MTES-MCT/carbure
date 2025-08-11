import { Button } from "common/components/button2"
import { CheckboxGroup, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"

export function ProductionSite() {
  const { t } = useTranslation()

  return (
    <EditableCard title={t("Caractéristiques du site de production")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => {}}>
          <RadioGroup
            readOnly={!isEditing}
            label={t("Type de voie")}
            options={[
              { value: "", label: t("Voie sèche") },
              { value: "", label: t("Voie liquide") },
            ]}
          />
          <RadioGroup
            readOnly={!isEditing}
            label={t("Procédé méthanisation")}
            options={[
              { value: "", label: t("Continu (infiniment mélangé)") },
              { value: "", label: t("En piston (semi-continu)") },
              { value: "", label: t("En silos (batch)") },
            ]}
          />
          <TextInput
            readOnly={!isEditing}
            type="number"
            label={t(
              "Rendement de l’installation de production de biométhane (%)"
            )}
            hintText={t(
              "Rendement global de l’installation (comprenant notamment le rendement de l’épurateur)"
            )}
          />
          <CheckboxGroup
            value={[]}
            onChange={() => {}}
            readOnly={!isEditing}
            label={t("Débitmètre présent sur votre installation :")}
            options={[
              {
                value: "",
                label: t("Débitmètre dédié à la production de biogaz"),
              },
              {
                value: "",
                label: t(
                  "Débitmètre dédié au volume de biogaz traité en épuration"
                ),
              },
              {
                value: "",
                label: t("Débitmètre dédié au volume de biogaz torché"),
              },
              {
                value: "",
                label: t(
                  "Débitmètre dédié au volume de biogaz ou biométhane utilisé pour le chauffage du digesteur"
                ),
              },
              {
                value: "",
                label: t(
                  "Compteur dédié à la consommation électrique au système d'épuration et traitement des évents"
                ),
              },
              {
                value: "",
                label: t(
                  "Compteur dédié à la consommation électrique de l'ensemble de l'unité de production"
                ),
              },
            ]}
          />
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t("Présence d’un hygiénisateur")}
              options={getYesNoOptions()}
              orientation="horizontal"
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Existence d’un procédé de valorisation du CO2 ?")}
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
