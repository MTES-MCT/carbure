import {
  components,
  HeatTypeEnum,
  IcpeRegimeEnum,
  ProductionTypeEnum,
} from "api-schema"
import { useTranslation } from "react-i18next"
import { useQuery, useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { api } from "common/services/api-fetch"
import { useNotify, useNotifyError } from "common/components/notifications"
import { LoaderOverlay, Grid } from "common/components/scaffold"
import {
  DateInput,
  NumberInput,
  RadioGroup,
  TextInput,
} from "common/components/inputs2"
import { Button } from "common/components/button2"
import { useForm } from "common/components/form2"
import { EditableCard } from "common/molecules/editable-card/editable-card"

type Installation = components["schemas"]["EnergyInstallation"]
type InstallationRequest = components["schemas"]["EnergyInstallationRequest"]

const getInstallation = async (entity_id: number) =>
  (
    await api.GET("/solid-biomass/energy-installation/", {
      params: { query: { entity_id } },
    })
  ).data

const saveInstallation = async (entity_id: number, data: InstallationRequest) =>
  (
    await api.PUT("/solid-biomass/energy-installation/", {
      params: { query: { entity_id } },
      body: data,
      bodySerializer: JSON.stringify,
      headers: { "Content-Type": "application/json" },
    })
  ).data

export default function EnergyInstallationPage() {
  const entity = useEntity()
  return <EnergyInstallationContent key={entity.id} />
}

function EnergyInstallationContent() {
  const entity = useEntity()
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { result, loading, error } = useQuery(getInstallation, {
    key: "energy-installation",
    params: [entity.id],
  })
  const mutation = useMutation(
    (data: InstallationRequest) => saveInstallation(entity.id, data),
    {
      invalidates: ["energy-installation"],
      onSuccess: () =>
        notify(t("L'installation a bien été sauvegardée."), {
          variant: "success",
        }),
      onError: (error) => notifyError(error),
    }
  )
  if (loading && !result) return <LoaderOverlay />
  if (error && !result)
    return <p>{t("Impossible de charger l'installation.")}</p>
  return (
    <InstallationCards
      installation={result ?? {}}
      readOnly={!entity.canWrite()}
      save={mutation.execute}
      loading={mutation.loading}
    />
  )
}

type CardProps = {
  installation: Installation
  readOnly: boolean
  save: (data: InstallationRequest) => Promise<unknown>
  loading: boolean
}

function InstallationCards(props: CardProps) {
  const { installation } = props
  const generalKey = JSON.stringify([
    installation.production_type,
    installation.heat_type,
    installation.commissioning_date,
    installation.useful_temperature,
    installation.electrical_efficiency,
    installation.thermal_efficiency,
  ])
  const icpeKey = JSON.stringify([
    installation.icpe_number,
    installation.icpe_regime,
  ])
  return (
    <>
      <GeneralCard key={generalKey} {...props} />
      <IcpeCard key={icpeKey} {...props} />
    </>
  )
}

function GeneralCard({ installation, readOnly, save, loading }: CardProps) {
  const { t } = useTranslation()
  const form = useForm<Installation>(installation)
  const { value, bind } = form
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
              readOnly={!isEditing}
              label={t("Date de mise en service")}
              {...bind("commissioning_date")}
            />
            {value.production_type === ProductionTypeEnum.COGENERATION && (
              <NumberInput
                readOnly={!isEditing}
                label={t("Température utile au point de fourniture (°C)")}
                step={0.1}
                {...bind("useful_temperature")}
              />
            )}
            {(value.production_type === ProductionTypeEnum.ELECTRICITY ||
              value.production_type === ProductionTypeEnum.COGENERATION) && (
              <NumberInput
                readOnly={!isEditing}
                label={t("Rendement électrique (%)")}
                min={0}
                max={100}
                step={0.1}
                {...bind("electrical_efficiency")}
              />
            )}
            {(value.production_type === ProductionTypeEnum.HEAT ||
              value.production_type === ProductionTypeEnum.COGENERATION) && (
              <NumberInput
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

function IcpeCard({ installation, readOnly, save, loading }: CardProps) {
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
