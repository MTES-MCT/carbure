import { HeatTypeEnum, ProductionTypeEnum } from "api-schema"
import { useTranslation } from "react-i18next"
import { Grid } from "common/components/scaffold"
import { DateInput, NumberInput, RadioGroup } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { useForm } from "common/components/form2"
import { EditableCard } from "common/molecules/editable-card/editable-card"
import { Installation, InstallationCardProps } from "../types"

export function GeneralCard({
  installation,
  readOnly,
  save,
  loading,
}: InstallationCardProps) {
  const { t } = useTranslation()
  const form = useForm<Installation>(installation)
  const { value, bind } = form

  const isCogeneration =
    value.production_type === ProductionTypeEnum.COGENERATION
  const producesElectricity =
    value.production_type === ProductionTypeEnum.ELECTRICITY || isCogeneration
  const producesHeat =
    value.production_type === ProductionTypeEnum.HEAT || isCogeneration

  const saveGeneral = () =>
    save({
      production_type: value.production_type ?? null,
      heat_type: value.heat_type ?? null,
      commissioning_date: value.commissioning_date || null,
      useful_temperature: value.useful_temperature ?? null,
      electrical_efficiency: value.electrical_efficiency ?? null,
      thermal_efficiency: value.thermal_efficiency ?? null,
    })

  return (
    <EditableCard
      title={t("Informations générales du site de production")}
      readOnly={readOnly}
      onCancel={() => form.setValue(installation)}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={saveGeneral}>
          <Grid cols={2} gap="lg">
            <RadioGroup
              required
              readOnly={!isEditing}
              label={t("Type de production")}
              options={[
                {
                  value: ProductionTypeEnum.ELECTRICITY,
                  label: t("Électricité seule"),
                },
                {
                  value: ProductionTypeEnum.HEAT,
                  label: t("Chaleur/Froid seul"),
                },
                {
                  value: ProductionTypeEnum.COGENERATION,
                  label: t("Cogénération"),
                },
              ]}
              {...bind("production_type")}
            />
            {value.production_type &&
              value.production_type !== ProductionTypeEnum.ELECTRICITY && (
                <RadioGroup
                  required
                  readOnly={!isEditing}
                  label={t("Type de production de chaleur")}
                  options={[
                    { value: HeatTypeEnum.HOT_WATER, label: t("Eau chaude") },
                    { value: HeatTypeEnum.STEAM, label: t("Vapeur") },
                    {
                      value: HeatTypeEnum.HOT_WATER_STEAM,
                      label: t("Eau chaude et vapeur"),
                    },
                    {
                      value: HeatTypeEnum.INDUSTRIAL_PROCESS,
                      label: t("Process industriel"),
                    },
                  ]}
                  {...bind("heat_type")}
                />
              )}
            <DateInput
              required
              readOnly={!isEditing}
              label={t("Date de mise en service")}
              {...bind("commissioning_date")}
            />
            {isCogeneration && (
              <NumberInput
                required
                readOnly={!isEditing}
                label={t("Température utile au point de fourniture (°C)")}
                step={0.1}
                {...bind("useful_temperature")}
              />
            )}
            {producesElectricity && (
              <NumberInput
                required
                readOnly={!isEditing}
                label={t("Rendement électrique (%)")}
                min={0}
                max={100}
                step={0.1}
                {...bind("electrical_efficiency")}
              />
            )}
            {producesHeat && (
              <NumberInput
                required
                readOnly={!isEditing}
                label={t("Rendement thermique (%)")}
                min={0}
                max={100}
                step={0.1}
                {...bind("thermal_efficiency")}
              />
            )}
          </Grid>
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
