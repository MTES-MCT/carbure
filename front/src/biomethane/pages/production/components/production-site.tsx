import { Button } from "common/components/button2"
import {
  CheckboxGroup,
  NumberInput,
  RadioGroup,
} from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { EditableCard } from "common/molecules/editable-card"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneProductionUnit,
  BiomethaneProductionUnitPatchRequest,
  ProcessType,
  MethanizationProcess,
} from "../types"
import { InstalledMetersEnum } from "api-schema"
import { useSaveProductionUnit } from "../production.hooks"

type ProductionSiteForm = DeepPartial<BiomethaneProductionUnitPatchRequest> & {
  installed_meters?: InstalledMetersEnum[]
}

export function ProductionSite({
  productionUnit,
}: {
  productionUnit?: BiomethaneProductionUnit
}) {
  const { t } = useTranslation()
  const { bind, value } = useForm<ProductionSiteForm>(productionUnit ?? {})

  const { execute: saveProductionUnit, loading } = useSaveProductionUnit()

  const processTypeOptions = [
    {
      label: t("Voie sèche"),
      value: ProcessType.DRY_PROCESS,
    },
    {
      label: t("Voie liquide"),
      value: ProcessType.LIQUID_PROCESS,
    },
  ]

  const methanizationProcessOptions = [
    {
      label: t("Continu (infiniment mélangé)"),
      value: MethanizationProcess.CONTINUOUS_INFINITELY_MIXED,
    },
    {
      label: t("En piston (semi-continu)"),
      value: MethanizationProcess.PLUG_FLOW_SEMI_CONTINUOUS,
    },
    {
      label: t("En silos (batch)"),
      value: MethanizationProcess.BATCH_SILOS,
    },
  ]

  const installedMetersOptions = [
    {
      value: InstalledMetersEnum.BIOGAS_PRODUCTION_FLOWMETER,
      label: t("Débitmètre dédié à la production de biogaz"),
    },
    {
      value: InstalledMetersEnum.PURIFICATION_FLOWMETER,
      label: t("Débitmètre dédié au volume de biogaz traité en épuration"),
    },
    {
      value: InstalledMetersEnum.FLARING_FLOWMETER,
      label: t("Débitmètre dédié au volume de biogaz torché"),
    },
    {
      value: InstalledMetersEnum.HEATING_FLOWMETER,
      label: t(
        "Débitmètre dédié au volume de biogaz ou biométhane utilisé pour le chauffage du digesteur"
      ),
    },
    {
      value: InstalledMetersEnum.PURIFICATION_ELECTRICAL_METER,
      label: t(
        "Compteur dédié à la consommation électrique au système d'épuration et traitement des évents"
      ),
    },
    {
      value: InstalledMetersEnum.GLOBAL_ELECTRICAL_METER,
      label: t(
        "Compteur dédié à la consommation électrique de l'ensemble de l'unité de production"
      ),
    },
  ]

  return (
    <EditableCard title={t("Caractéristiques du site de production")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => saveProductionUnit(value!)}>
          <RadioGroup
            readOnly={!isEditing}
            label={t("Type de voie")}
            options={processTypeOptions}
            {...bind("process_type")}
          />
          <RadioGroup
            readOnly={!isEditing}
            label={t("Procédé méthanisation")}
            options={methanizationProcessOptions}
            {...bind("methanization_process")}
          />
          <NumberInput
            readOnly={!isEditing}
            label={t(
              "Rendement de l'installation de production de biométhane (%)"
            )}
            hintText={t(
              "Rendement global de l'installation (comprenant notamment le rendement de l'épurateur)"
            )}
            {...bind("production_efficiency")}
          />
          <CheckboxGroup
            readOnly={!isEditing}
            label={t("Débitmètre présent sur votre installation :")}
            options={installedMetersOptions}
            {...bind("installed_meters")}
          />
          <Grid cols={2} gap="lg">
            <RadioGroup
              readOnly={!isEditing}
              label={t("Présence d'un hygiénisateur")}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_hygienization_unit")}
            />
            <RadioGroup
              readOnly={!isEditing}
              label={t("Existence d'un procédé de valorisation du CO2 ?")}
              options={getYesNoOptions()}
              orientation="horizontal"
              {...bind("has_co2_valorization_process")}
            />
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
