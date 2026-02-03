import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useTranslation } from "react-i18next"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import { BiomethaneEnergy, BiomethaneEnergyInputRequest } from "../../types"
import { useSaveEnergy } from "../../energy.hooks"
import { BiomethaneContract } from "biomethane/pages/contract/types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useInjectedBiomethane } from "./injected-biomethane.hooks"
import { CONVERSIONS } from "common/utils/formatters"

export type InjectedBiomethaneForm = DeepPartial<
  Pick<
    BiomethaneEnergyInputRequest,
    | "injected_biomethane_gwh_pcs_per_year"
    // | "injected_biomethane_nm3_per_year"
    | "injected_biomethane_ch4_rate_percent"
    | "injected_biomethane_pcs_kwh_per_nm3"
    // | "operating_hours"
  >
>
const extractValues = (energy?: InjectedBiomethaneForm) => {
  return {
    injected_biomethane_gwh_pcs_per_year:
      energy?.injected_biomethane_gwh_pcs_per_year,
    // injected_biomethane_nm3_per_year: energy?.injected_biomethane_nm3_per_year,
    injected_biomethane_ch4_rate_percent:
      energy?.injected_biomethane_ch4_rate_percent,
    injected_biomethane_pcs_kwh_per_nm3:
      energy?.injected_biomethane_pcs_kwh_per_nm3,
    // operating_hours: energy?.operating_hours,
  }
}
export function InjectedBiomethane({
  contract,
  energy,
}: {
  contract?: BiomethaneContract
  energy?: BiomethaneEnergy
}) {
  const { t } = useTranslation()
  const { bind, value } = useFormContext<InjectedBiomethaneForm>()
  const saveEnergy = useSaveEnergy()
  const { canEditDeclaration } = useAnnualDeclaration()
  const { rule, operatingHours, injectedBiomethaneNm3PerYear } =
    useInjectedBiomethane(energy?.monthly_reports ?? [], contract)

  const handleSave = async () => saveEnergy.execute(extractValues(value))
  return (
    <ManagedEditableCard
      sectionId="injected-biomethane"
      title={t("Biométhane injecté dans le réseau")}
      description={t(
        "Ces informations concernent la production finale de biométhane de votre installation"
      )}
      readOnly={!canEditDeclaration}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={handleSave}>
          <NumberInput
            readOnly={!isEditing}
            label={t("Quantité de biométhane injecté (GWhPCS/an)")}
            type="number"
            {...bind("injected_biomethane_gwh_pcs_per_year")}
            required
          />
          <NumberInput
            readOnly={!isEditing}
            label={t("PCS du biométhane injecté (kWh/Nm3)")}
            hintText={t("Valeur moyenne de l'année de déclaration")}
            type="number"
            {...bind("injected_biomethane_pcs_kwh_per_nm3")}
            required
          />

          <NumberInput
            readOnly={!isEditing}
            label={t("Quantité de biométhane injecté (Nm3/an)")}
            hasTooltip
            title={t(
              "Quantité de biométhane injecté (Nm3/an) = Quantité de biométhane injecté (GWhPCS/an) * PCS du biométhane injecté (kWh/Nm3) * 10^-6"
            )}
            type="number"
            value={injectedBiomethaneNm3PerYear}
            disabled
          />

          <div />

          <NumberInput
            readOnly={!isEditing}
            label={t("Taux de CH4 dans le biométhane injecté (%)")}
            hintText={t("Valeur moyenne de l'année de déclaration")}
            type="number"
            min={0}
            max={100}
            step={0.1}
            {...bind("injected_biomethane_ch4_rate_percent")}
            required
          />

          <NumberInput
            label={t("Nombre d'heures de fonctionnement (h)")}
            hintText={t(
              "Fonctionnement à plein régime (à la capacité maximale inscrite dans le contrat)"
            )}
            value={operatingHours}
            disabled
            required
            readOnly={!isEditing}
            hasTooltip
            title={rule}
            max={CONVERSIONS.hours.yearsToHours(1)}
          />
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
