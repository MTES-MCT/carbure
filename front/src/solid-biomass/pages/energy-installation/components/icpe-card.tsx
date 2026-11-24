import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { useForm } from "common/components/form2"
import { EditableCard } from "common/molecules/editable-card/editable-card"
import { IcpeNumberField } from "common/molecules/sites/icpe-number-field"
import { IcpeRegimeField } from "common/molecules/sites/icpe-regime-field"
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
          <IcpeNumberField readOnly={!isEditing} {...bind("icpe_number")} />
          <IcpeRegimeField readOnly={!isEditing} {...bind("icpe_regime")} />

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
