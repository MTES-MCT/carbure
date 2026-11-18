import { IcpeRegimeEnum } from "api-schema"
import { useTranslation } from "react-i18next"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { useForm } from "common/components/form2"
import { EditableCard } from "common/molecules/editable-card/editable-card"
import { Installation, InstallationCardProps } from "../types"

export function IcpeCard({
  installation,
  readOnly,
  save,
  loading,
}: InstallationCardProps) {
  const { t } = useTranslation()
  const form = useForm<Installation>(installation)

  const { value, bind } = form

  return (
    <EditableCard
      title={t("ICPE")}
      readOnly={readOnly}
      onCancel={() => form.setValue(installation)}
    >
      {({ isEditing }) => (
        <EditableCard.Form
          onSubmit={() =>
            save({
              icpe_number: value.icpe_number || null,
              icpe_regime: value.icpe_regime ?? null,
            })
          }
        >
          <TextInput
            readOnly={!isEditing}
            label={t("N° ICPE")}
            pattern="[0-9]{10}"
            {...bind("icpe_number")}
          />
          <RadioGroup
            readOnly={!isEditing}
            label={t("Régime ICPE")}
            options={[
              {
                value: IcpeRegimeEnum.AUTHORIZATION,
                label: t("Autorisation"),
              },
              {
                value: IcpeRegimeEnum.REGISTRATION,
                label: t("Enregistrement"),
              },
              {
                value: IcpeRegimeEnum.DECLARATION_PERIODIC_CONTROLS,
                label: t("Déclaration (avec contrôles périodiques)"),
              },
            ]}
            {...bind("icpe_regime")}
          />
          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
