import { Button } from "common/components/button2"
import { NumberInput, RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  BiomethaneEnergy,
  BiomethaneEnergyInputRequest,
  EnergyType,
} from "../../types"
import { useSaveEnergy } from "../../energy.hooks"
import {
  BiomethaneContract,
  TariffReference,
} from "biomethane/pages/contract/types"
import {
  useBiogazOrBiomethaneAutoconsumptionLabel,
  useEnergyEfficiencyCoefficient,
} from "./energy-efficiency.hooks"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { getYesNoOptions } from "common/utils/normalizers"

type EnergyEfficiencyForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "purified_biogas_quantity_nm3"
    | "purification_electric_consumption_kwe"
    | "self_consumed_biogas_nm3"
    | "self_consumed_biogas_or_biomethane_kwh"
    | "total_unit_electric_consumption_kwe"
    | "butane_or_propane_addition"
    | "fossil_fuel_consumed_kwh"
  >
>
const extractValues = (energy?: EnergyEfficiencyForm) => {
  return {
    purified_biogas_quantity_nm3: energy?.purified_biogas_quantity_nm3,
    purification_electric_consumption_kwe:
      energy?.purification_electric_consumption_kwe,
    total_unit_electric_consumption_kwe:
      energy?.total_unit_electric_consumption_kwe,
    self_consumed_biogas_nm3: energy?.self_consumed_biogas_nm3,
    self_consumed_biogas_or_biomethane_kwh:
      energy?.self_consumed_biogas_or_biomethane_kwh,
    butane_or_propane_addition: energy?.butane_or_propane_addition,
    fossil_fuel_consumed_kwh: energy?.fossil_fuel_consumed_kwh,
  }
}
export function EnergyEfficiency({
  energy,
  contract,
}: {
  energy?: BiomethaneEnergy
  contract?: BiomethaneContract
}) {
  const { t } = useTranslation()

  const { bind, value } = useFormContext<EnergyEfficiencyForm>()
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()

  const handleSubmit = async () => saveEnergy.execute(extractValues(value))

  const isTariffReference2023 =
    contract?.tariff_reference === TariffReference.Value2023

  const energyEfficiencyCoefficient = useEnergyEfficiencyCoefficient({
    purified_biogas_quantity_nm3: value.purified_biogas_quantity_nm3 ?? 0,
    purification_electric_consumption_kwe:
      value.purification_electric_consumption_kwe ?? 0,
    total_unit_electric_consumption_kwe:
      value.total_unit_electric_consumption_kwe ?? 0,
    tariff_reference: contract?.tariff_reference,
    injected_biomethane_gwh_pcs_per_year:
      energy?.injected_biomethane_gwh_pcs_per_year ?? 0,
  })

  const biogazOrBiomethaneAutoconsumptionLabel =
    useBiogazOrBiomethaneAutoconsumptionLabel(contract?.tariff_reference)

  return (
    <ManagedEditableCard
      sectionId="energy-efficiency"
      title={t("Efficacité énergétique")}
      description={t(
        "Ces informations permettent de vérifier le respect des obligations en termes d'efficacité énergétique"
      )}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={handleSubmit}>
          <Grid cols={1} gap="lg">
            {energyTypesIncludesBiogazOrBiomethane(energy?.energy_types) && (
              <NumberInput
                readOnly={!isEditing}
                label={biogazOrBiomethaneAutoconsumptionLabel}
                {...bind("self_consumed_biogas_or_biomethane_kwh")}
                required
                step={0.01}
              />
            )}
            {!isTariffReference2023 && (
              <>
                <NumberInput
                  readOnly={!isEditing}
                  label={t(
                    "Quantité totale de biogaz traitée par le système d'épuration sur l'année (Nm3)"
                  )}
                  {...bind("purified_biogas_quantity_nm3")}
                  required
                />
                <NumberInput
                  readOnly={!isEditing}
                  label={t(
                    "Consommation électrique du système d'épuration et le cas échéant du traitement des évents (kWe)"
                  )}
                  hintText={t(
                    "Le système d'épuration comprend les unités fonctionnelles de désulfuration, décarbonation et séchage du biogaz, qu'elles soient séparées au cours du processus d'épuration ou non."
                  )}
                  {...bind("purification_electric_consumption_kwe")}
                  required
                />
              </>
            )}
            {isTariffReference2023 && (
              <>
                <NumberInput
                  readOnly={!isEditing}
                  label={t(
                    "Quantité de biogaz autoconsommée pour la pasteurisation, l'hygiénisation ou le traitement des intrants, le chauffage du digesteur et l'épuration du biogaz (Nm3)"
                  )}
                  {...bind("self_consumed_biogas_nm3")}
                  required
                />
                <NumberInput
                  readOnly={!isEditing}
                  label={t(
                    "Consommation électrique soutirée pour l'ensemble de l'unité (kWe)"
                  )}
                  hintText={t(
                    "Consommation d’électricité soutirée sur le réseau public d’électricité d’une installation de production de biométhane, cumulée le cas échéant avec la consommation de l’installation d’injection associée"
                  )}
                  {...bind("total_unit_electric_consumption_kwe")}
                  required
                />
              </>
            )}

            <Grid cols={2} gap="lg">
              <RadioGroup
                readOnly={!isEditing}
                label={t(
                  "Addition de butane ou propane lors de l'injection du biométhane dans le réseau"
                )}
                {...bind("butane_or_propane_addition")}
                required
                options={getYesNoOptions()}
                orientation="horizontal"
              />
              <NumberInput
                readOnly={!isEditing}
                label={t("Quantité de combustible fossile consommé (kWh)")}
                {...bind("fossil_fuel_consumed_kwh")}
                required
              />
            </Grid>

            <TextInput
              label={t("Coefficient d'efficacité énergétique")}
              readOnly={!isEditing}
              disabled
              value={energyEfficiencyCoefficient.label}
              state={energyEfficiencyCoefficient.error ? "info" : "default"}
              stateRelatedMessage={energyEfficiencyCoefficient.error}
              hasTooltip
              title={energyEfficiencyCoefficient.tooltip}
            />
          </Grid>

          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={saveEnergy.loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}

const energyTypesIncludesBiogazOrBiomethane = (energyTypes?: EnergyType[]) =>
  energyTypes?.includes(EnergyType.PRODUCED_BIOGAS) ||
  energyTypes?.includes(EnergyType.PRODUCED_BIOMETHANE)
