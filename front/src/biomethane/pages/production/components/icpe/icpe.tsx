import { Button } from "common/components/button2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"

export function ICPE() {
  const { t } = useTranslation()

  return (
    <EditableCard title={t("ICPE")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => {}}>
          <TextInput
            readOnly={!isEditing}
            label={t("N° ICPE")}
            state="info"
            stateRelatedMessage={t("Code à 10 chiffres")}
          />
          <RadioGroup
            readOnly={!isEditing}
            label={t("Régime ICPE")}
            orientation="horizontal"
            options={[
              { value: "", label: t("Autorisation") },
              { value: "", label: t("Enregistrement") },
              {
                value: "",
                label: t("Déclaration (avec contrôles périodiques)"),
              },
            ]}
          />
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
